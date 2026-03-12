from django.conf import settings
from django.contrib import admin, messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.urls import path, reverse

from clients.models import Email as EmailBase
from clients.models import Lead as LeadBase

from .models import Email, HighSchool, Lead, SocialMessage


for model in (LeadBase, EmailBase):
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass


class EmailInline(admin.TabularInline):
    model = EmailBase
    extra = 0
    readonly_fields = ("sent_at",)


class SocialMessageInline(admin.TabularInline):
    model = SocialMessage
    extra = 0
    readonly_fields = ("received_at",)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "high_school", "preferred_campus", "preferred_site", "created_at")
    search_fields = ("name", "email")
    list_filter = ("preferred_campus", "preferred_site", "high_school", "converted")
    inlines = [EmailInline, SocialMessageInline]
    change_form_template = "admin/lead_change_form.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "dashboard/",
                self.admin_site.admin_view(self.dashboard_view),
                name="admissions_dashboard",
            ),
            path(
                "<int:lead_id>/responder/",
                self.admin_site.admin_view(self.responder_view),
                name="lead_responder",
            )
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        context = dict(
            self.admin_site.each_context(request),
            total_leads=LeadBase.objects.count(),
            total_leads_convertidos=LeadBase.objects.filter(converted=True).count(),
            total_leads_pendientes=LeadBase.objects.filter(converted=False).count(),
            total_correos_enviados=EmailBase.objects.filter(direction="outbound").count(),
            total_social_messages=SocialMessage.objects.count(),
            recent_leads=LeadBase.objects.select_related("preferred_campus", "preferred_site", "high_school").order_by("-created_at")[:8],
            recent_emails=EmailBase.objects.select_related("lead").order_by("-sent_at")[:8],
            recent_social_messages=SocialMessage.objects.select_related("lead").order_by("-received_at")[:8],
        )
        return TemplateResponse(request, "admin/admissions_dashboard.html", context)

    def responder_view(self, request, lead_id):
        lead = get_object_or_404(LeadBase, pk=lead_id)

        if request.method == "POST":
            mensaje = request.POST.get("mensaje")

            send_mail(
                subject="Respuesta a tu consulta",
                message=mensaje,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[lead.email],
                fail_silently=False,
            )

            EmailBase.objects.create(
                lead=lead,
                subject="Respuesta a tu consulta",
                body=mensaje,
                direction="outbound",
            )

            messages.success(request, "Correo enviado al lead correctamente")
            return redirect(reverse("admin:admissions_lead_change", args=[lead.id]))

        return render(request, "admin/responder_lead.html", {"lead": lead})


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ("lead", "subject", "direction", "sent_at")
    search_fields = ("lead__name", "lead__email", "subject")
    list_filter = ("direction", "sent_at")


@admin.register(HighSchool)
class HighSchoolAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "department", "active")
    search_fields = ("name", "city", "department")
    list_filter = ("active", "department")


@admin.register(SocialMessage)
class SocialMessageAdmin(admin.ModelAdmin):
    list_display = ("network", "author_name", "lead", "received_at")
    search_fields = ("author_name", "author_handle", "message", "lead__name", "lead__email")
    list_filter = ("network", "received_at")
