import logging

from admissions.models import HighSchool, SocialMessage
from commercial.models import AcademicOffer
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Client, Email, Lead, Opportunity, Product
from .serializers import (
    ClientSerializer,
    AcademicOfferSerializer,
    HighSchoolSerializer,
    LeadSerializer,
    OpportunitySerializer,
    ProductSerializer,
    SocialMessageSerializer,
)

logger = logging.getLogger(__name__)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]


class OpportunityViewSet(viewsets.ModelViewSet):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    permission_classes = [IsAuthenticated]


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.prefetch_related("notes").order_by("-created_at")
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ["name", "email", "company"]
    ordering_fields = ["created_at", "name"]
    filterset_fields = ["status"]


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]

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
                direction="outbound",
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


class HighSchoolViewSet(viewsets.ModelViewSet):
    queryset = HighSchool.objects.all()
    serializer_class = HighSchoolSerializer
    permission_classes = [IsAuthenticated]


class SocialMessageViewSet(viewsets.ModelViewSet):
    queryset = SocialMessage.objects.select_related("lead").all()
    serializer_class = SocialMessageSerializer
    permission_classes = [IsAuthenticated]


class AcademicOfferViewSet(viewsets.ModelViewSet):
    queryset = AcademicOffer.objects.select_related(
        "program",
        "campus",
        "site",
        "faculty",
        "academic_degree",
        "academic_period",
    ).order_by("-id")
    serializer_class = AcademicOfferSerializer
    permission_classes = [IsAuthenticated]
