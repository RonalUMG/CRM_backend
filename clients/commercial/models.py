from django.core.exceptions import ValidationError
from django.db import models

from academics.models import AcademicDegree, AcademicPeriod, Faculty
from clients.models import Campus, Product, Site
from clients.models import Opportunity as OpportunityBase
from clients.models import Product as ProductBase


class Product(ProductBase):
    class Meta:
        proxy = True
        app_label = "commercial"
        verbose_name = "Programa"
        verbose_name_plural = "Programas"


class Opportunity(OpportunityBase):
    class Meta:
        proxy = True
        app_label = "commercial"
        verbose_name = "Oportunidad"
        verbose_name_plural = "Oportunidades"


class AcademicOffer(models.Model):
    program = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="academic_offers")
    campus = models.ForeignKey(Campus, null=True, blank=True, on_delete=models.SET_NULL, related_name="academic_offers")
    site = models.ForeignKey(Site, null=True, blank=True, on_delete=models.SET_NULL, related_name="academic_offers")
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="academic_offers")
    academic_degree = models.ForeignKey(AcademicDegree, on_delete=models.CASCADE, related_name="academic_offers")
    academic_period = models.ForeignKey(AcademicPeriod, on_delete=models.CASCADE, related_name="academic_offers")
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Oferta Academica"
        verbose_name_plural = "Ofertas Academicas"
        unique_together = (
            "program",
            "campus",
            "site",
            "faculty",
            "academic_degree",
            "academic_period",
        )

    def clean(self):
        if not self.campus and not self.site:
            raise ValidationError("Debes definir campus o sitio para la oferta academica.")
        if self.site and self.campus and self.site.campus_id != self.campus_id:
            raise ValidationError("El sitio seleccionado no pertenece al campus indicado.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        campus_or_site = self.site.name if self.site else self.campus.name
        return f"{self.program.name} | {self.faculty.name} | {self.academic_period.name} | {campus_or_site}"
