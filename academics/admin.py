from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path

from clients.models import Campus as CampusBase
from clients.models import Site as SiteBase

from .models import AcademicDegree, AcademicPeriod, Campus, Faculty, Site


for model in (CampusBase, SiteBase):
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "country", "is_central")
    search_fields = ("name", "city", "country")
    list_filter = ("country", "is_central")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("dashboard/", self.admin_site.admin_view(self.dashboard_view), name="academics_dashboard")
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        context = dict(
            self.admin_site.each_context(request),
            total_campus=CampusBase.objects.count(),
            total_campus_centrales=CampusBase.objects.filter(is_central=True).count(),
            total_sites=SiteBase.objects.count(),
            recent_campus=CampusBase.objects.order_by("-id")[:8],
            recent_sites=SiteBase.objects.select_related("campus").order_by("-id")[:8],
        )
        return TemplateResponse(request, "admin/academics_dashboard.html", context)


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("name", "campus", "city", "site_type")
    search_fields = ("name", "city", "campus__name")
    list_filter = ("campus", "site_type")


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "active")
    search_fields = ("name", "code")
    list_filter = ("active",)


@admin.register(AcademicPeriod)
class AcademicPeriodAdmin(admin.ModelAdmin):
    list_display = ("name", "period_type", "start_date", "end_date", "active")
    search_fields = ("name",)
    list_filter = ("period_type", "active")


@admin.register(AcademicDegree)
class AcademicDegreeAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "active")
    search_fields = ("name",)
    list_filter = ("level", "active")
