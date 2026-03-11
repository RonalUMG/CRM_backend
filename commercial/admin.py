from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path

from clients.models import Opportunity as OpportunityBase
from clients.models import Product as ProductBase

from .models import AcademicOffer, Opportunity, Product


for model in (ProductBase, OpportunityBase):
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "active")
    list_filter = ("active",)
    search_fields = ("name",)
    list_editable = ("price", "active")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("dashboard/", self.admin_site.admin_view(self.dashboard_view), name="commercial_dashboard")
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        context = dict(
            self.admin_site.each_context(request),
            total_products=ProductBase.objects.count(),
            total_products_activos=ProductBase.objects.filter(active=True).count(),
            total_opportunities=OpportunityBase.objects.count(),
            total_opportunities_won=OpportunityBase.objects.filter(status="won").count(),
            total_academic_offers=AcademicOffer.objects.count(),
            recent_products=ProductBase.objects.order_by("-id")[:8],
            recent_opportunities=OpportunityBase.objects.select_related("client", "product").order_by("-id")[:8],
            recent_academic_offers=AcademicOffer.objects.select_related(
                "program",
                "campus",
                "site",
                "faculty",
                "academic_degree",
                "academic_period",
            ).order_by("-id")[:8],
        )
        return TemplateResponse(request, "admin/commercial_dashboard.html", context)


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ("client", "product", "status", "amount")
    list_filter = ("status",)
    search_fields = ("client__name", "product__name")


@admin.register(AcademicOffer)
class AcademicOfferAdmin(admin.ModelAdmin):
    list_display = (
        "program",
        "faculty",
        "academic_degree",
        "academic_period",
        "campus",
        "site",
        "active",
    )
    list_filter = ("faculty", "academic_degree", "academic_period", "campus", "active")
    search_fields = (
        "program__name",
        "faculty__name",
        "academic_period__name",
        "campus__name",
        "site__name",
    )
