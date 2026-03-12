from django.db import models

from clients.models import Email as EmailBase
from clients.models import Lead as LeadBase


class Lead(LeadBase):
    class Meta:
        proxy = True
        app_label = "admissions"
        verbose_name = "Posible Cliente"
        verbose_name_plural = "Posibles Clientes"


class Email(EmailBase):
    class Meta:
        proxy = True
        app_label = "admissions"
        verbose_name = "Correo de Prospecto"
        verbose_name_plural = "Correos de Prospectos"


class HighSchool(models.Model):
    name = models.CharField(max_length=150, unique=True)
    city = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Colegio"
        verbose_name_plural = "Colegios"

    def __str__(self):
        return self.name


class SocialMessage(models.Model):
    NETWORK_CHOICES = [
        ("facebook", "Facebook"),
        ("instagram", "Instagram"),
        ("x", "X"),
    ]

    lead = models.ForeignKey(LeadBase, null=True, blank=True, on_delete=models.SET_NULL, related_name="social_messages")
    network = models.CharField(max_length=20, choices=NETWORK_CHOICES)
    author_name = models.CharField(max_length=150, blank=True)
    author_handle = models.CharField(max_length=150, blank=True)
    message = models.TextField()
    post_url = models.URLField(blank=True)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mensaje Social"
        verbose_name_plural = "Social"
        ordering = ("-received_at",)

    def __str__(self):
        return f"{self.get_network_display()} - {self.author_name or 'Anonimo'}"
