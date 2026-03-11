from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path

from clients.models import Client as ClientBase
from clients.models import Lead, Note as NoteBase, Opportunity, Product

from .models import Client, Note

admin.site.index_template = "admin/custom_index.html"


for model in (ClientBase, NoteBase):
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass


class NoteInline(admin.TabularInline):
    model = NoteBase
    extra = 1
    readonly_fields = ("created_at",)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "email")
    search_fields = ("name",)
    inlines = [NoteInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("dashboard/", self.admin_site.admin_view(self.dashboard_view), name="crm_dashboard")
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        total_clients = ClientBase.objects.count()
        total_notes = NoteBase.objects.count()
        total_leads = Lead.objects.count()
        total_opportunities = Opportunity.objects.count()
        total_products = Product.objects.filter(active=True).count()

        recent_clients = ClientBase.objects.order_by("-id")[:5]
        recent_notes = NoteBase.objects.order_by("-created_at")[:5]
        recent_leads = Lead.objects.order_by("-created_at")[:5]
        recent_opportunities = Opportunity.objects.order_by("-id")[:5]

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


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("client", "content", "created_at")
