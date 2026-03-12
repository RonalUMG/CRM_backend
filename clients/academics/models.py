from django.db import models

from clients.models import Campus as CampusBase
from clients.models import Site as SiteBase


class Campus(CampusBase):
    class Meta:
        proxy = True
        app_label = "academics"
        verbose_name = "Campus"
        verbose_name_plural = "Campus"


class Site(SiteBase):
    class Meta:
        proxy = True
        app_label = "academics"
        verbose_name = "Sitio"
        verbose_name_plural = "Sitios"


class Faculty(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=20, unique=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Facultad"
        verbose_name_plural = "Facultades"

    def __str__(self):
        return self.name


class AcademicPeriod(models.Model):
    PERIOD_TYPE_CHOICES = [
        ("semester", "Semestre"),
        ("quarter", "Trimestre"),
        ("annual", "Anual"),
    ]

    name = models.CharField(max_length=100, unique=True)
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPE_CHOICES, default="semester")
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Periodo Academico"
        verbose_name_plural = "Periodos Academicos"

    def __str__(self):
        return self.name


class AcademicDegree(models.Model):
    DEGREE_LEVEL_CHOICES = [
        ("technical", "Tecnico"),
        ("bachelor", "Licenciatura"),
        ("master", "Maestria"),
        ("doctorate", "Doctorado"),
    ]

    name = models.CharField(max_length=100, unique=True)
    level = models.CharField(max_length=20, choices=DEGREE_LEVEL_CHOICES)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Grado Academico"
        verbose_name_plural = "Grados Academicos"

    def __str__(self):
        return self.name
