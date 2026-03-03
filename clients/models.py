from django.db import models

class Client(models.Model):

    STATUS_CHOICES = [
        ('prospect', 'Prospecto'),
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
    ]

    name = models.CharField(max_length=100)
    company = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='prospect')
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Normalizamos email
        if self.email:
            self.email = self.email.strip().lower()

    def save(self, *args, **kwargs):
        self.full_clean()  # Ejecuta clean() y validaciones
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Note(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Nota para {self.client.name}: {self.content[:20]}"

class Lead(models.Model):
    name = models.CharField(max_length=225)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    converted = models.BooleanField(default=False)

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
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('proposal', 'Proposal Sent'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    ]


    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='new')
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.client.name} | {self.product.name} | {self.status}"
    
class Email(models.Model):

    DIRECTION_CHOICES = (
        ('in', 'Entrada'),
        ('out', 'Salida'),
    )

    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, related_name='emails')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    direction = models.CharField(max_length=3, choices=DIRECTION_CHOICES)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.get_direction_display()}"
