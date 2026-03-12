import re
from django.db import models
from django.core.exceptions import ValidationError


class Campus(models.Model):
    name = models.CharField(max_length=150, unique=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="Guatemala")
    is_central = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.city})"


class Site(models.Model):
    SITE_TYPE_CHOICES = [
        ("main", "Sede principal"),
        ("subsite", "Subsede"),
    ]

    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="sites")
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    site_type = models.CharField(
        max_length=20, choices=SITE_TYPE_CHOICES, default="main"
    )

    class Meta:
        unique_together = ("campus", "name")

    def __str__(self):
        return f"{self.name} - {self.campus.name}"

class Client(models.Model):
    STATUS_CHOICES = [
        ("prospect", "Prospecto"),
        ("active", "Activo"),
        ("inactive", "Inactivo"),
    ]

    name = models.CharField(max_length=100)
    company = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=8)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="prospect"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):

        # normalizar email
        if self.email:
            self.email = self.email.strip().lower()

        # validar telefono
        if self.phone:
            phone_regex = r"^\d{8}$"  # exactamente 8 digitos
            if not re.match(phone_regex, self.phone):
                raise ValidationError(
                    {"phone": "El telefono debe tener exactamente 8 digitos."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Note(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="notes"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Nota para {self.client.name}: {self.content[:20]}"


class Lead(models.Model):
    name = models.CharField(max_length=225)
    email = models.EmailField()
    phone = models.CharField(max_length=8, blank=True)
    message = models.TextField()
    preferred_campus = models.ForeignKey(
        Campus,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="leads",
    )
    preferred_site = models.ForeignKey(
        Site,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="leads",
    )
    high_school = models.ForeignKey(
        "admissions.HighSchool",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="leads",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    converted = models.BooleanField(default=False)

    def clean(self):
        if self.email:
            self.email = self.email.strip().lower()

        if self.phone:
            phone_regex = r"^\d{8}$"
            if not re.match(phone_regex, self.phone):
                raise ValidationError(
                    {"phone": "El telefono debe tener exactamente 8 digitos."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.email}"


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Opportunity(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("proposal", "Proposal Sent"),
        ("won", "Won"),
        ("lost", "Lost"),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default="new"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.client.name} | {self.product.name} | {self.status}"


class Email(models.Model):
    DIRECTION_CHOICES = (
        ("inbound", "Entrada"),
        ("outbound", "Salida"),
    )

    lead = models.ForeignKey("Lead", on_delete=models.CASCADE, related_name="emails")
    subject = models.CharField(max_length=255)
    body = models.TextField()
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sent_at"]

    def __str__(self):
        return f"{self.subject} - {self.get_direction_display()}"

