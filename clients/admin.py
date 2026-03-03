from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

from .models import Client, Note, Lead, Product, Opportunity, Email


class NoteInline(admin.TabularInline):
    model = Note
    extra = 1
    readonly_fields = ('created_at',)

class EmailInline(admin.TabularInline):
    model = Email
    extra = 0
    readonly_fields = ('sent_at',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name',)
    inlines = [NoteInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("dashboard/", self.admin_site.admin_view(self.dashboard_view))
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        total_clients = Client.objects.count()
        total_notes = Note.objects.count()
        total_leads = Lead.objects.count()
        total_opportunities = Opportunity.objects.count()
        total_products = Product.objects.filter(active=True).count()

        recent_clients = Client.objects.order_by('-id')[:5]
        recent_notes = Note.objects.order_by('-created_at')[:5]
        recent_leads = Lead.objects.order_by('-created_at')[:5]
        recent_opportunities = Opportunity.objects.order_by('-id')[:5]

        context = dict(
            self.admin_site.each_context(request),
            total_clients=total_clients,
            total_notes=total_notes,
            total_leads=total_leads,
            total_opportunities=total_opportunities,
            total_products=total_products,
            recent_clients=recent_clients,
            recent_notes=recent_notes,
            recent_leads=recent_leads,
            recent_opportunities=recent_opportunities,
        )

        return TemplateResponse(request, "admin/panel.html", context)
    
@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email')
    inlines = [EmailInline]
    change_form_template = "admin/lead_change_form.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls =[
            path(
                '<int:lead_id>/responder/',
                self.admin_site.admin_view(self.responder_view),
                name='lead_responder',
            )
        ]
        return custom_urls + urls
    
    def responder_view(self, request, lead_id):
        lead = get_object_or_404(Lead, pk=lead_id)

        if request.method == "POST":
            mensaje = request.POST.get("mensaje")
 
            send_mail(
                subject="Respuesta a tu consulta",
                message=mensaje,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[lead.email],
                fail_silently=False,
            )

            Email.objects.create(
                lead=lead,
                subject="Respuesta a tu consulta",
                body=mensaje,
                direction='out'
            )

            lead.status ='prospect'
            lead.save()

            messages.success(request, "Correo enviado y lead convertido a prospecto")
            return redirect(reverse("admin:clients_lead_change", args=[lead.id]))
        return render(request, "admin/responder_lead.html", {"lead": lead})


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'active')
    list_filter = ('active',)
    search_fields = ('name',)
    list_editable = ('price', 'active')
    

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('client', 'product', 'status', 'amount')
    list_filter = ('status',)
    search_fields = ('client__name', 'product__name')
    autocomplete_fields = ('client', 'product')


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('client', 'content', 'created_at')
# Register your models here.
