import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Client, Email, Lead, Opportunity, Product
from .serializers import (
    ClientSerializer,
    LeadSerializer,
    OpportunitySerializer,
    ProductSerializer,
)

logger = logging.getLogger(__name__)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OpportunityViewSet(viewsets.ModelViewSet):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.prefetch_related("notes").all()
    serializer_class = ClientSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ["name", "email", "company"]
    ordering_fields = ["created_at", "name"]
    filterset_fields = ["status"]


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer

    def perform_create(self, serializer):
        lead = serializer.save()

        try:
            send_mail(
                subject="Nuevo Lead recibido",
                message=f"""
Nuevo lead:
Nombre: {lead.name}
Email: {lead.email}
Mensaje: {lead.message}
""",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )

            Email.objects.create(
                lead=lead,
                subject="Nuevo Lead recibido",
                body=f"""
Nuevo lead:
Nombre: {lead.name}
Email: {lead.email}
Mensaje: {lead.message}
""",
                direction="out",
            )
        except Exception:
            logger.exception("Error enviando correo para lead_id=%s", lead.id)

    @action(detail=True, methods=["post"])
    def convert(self, request, pk=None):
        lead = self.get_object()

        if lead.converted:
            return Response(
                {"message": "Este lead ya fue convertido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not (lead.phone or "").strip():
            return Response(
                {"message": "No se puede convertir: el lead no tiene telefono."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        normalized_email = (lead.email or "").strip().lower()
        try:
            with transaction.atomic():
                Client.objects.get_or_create(
                    email=normalized_email,
                    defaults={
                        "name": lead.name,
                        "phone": lead.phone,
                        "status": "prospect",
                    },
                )

                lead.converted = True
                lead.save(update_fields=["converted"])
        except ValidationError as exc:
            return Response(
                {"message": "No se pudo convertir el lead.", "errors": exc.message_dict},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            send_mail(
                subject="Gracias por contactarnos",
                message=f"""
Hola {lead.name},

Gracias por tu interes.
Ya eres parte de nuestra base de clientes.

Pronto nos pondremos en contacto contigo.
                """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[lead.email],
            )
        except Exception:
            logger.exception("Error enviando correo de conversion para lead_id=%s", lead.id)

        return Response(
            {"message": "Lead convertido correctamente."},
            status=status.HTTP_200_OK,
        )
