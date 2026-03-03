from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Client, Lead
from .serializers import ClientSerializer


class ClientSerializerValidationTests(TestCase):
    def test_accepts_non_gmail_email(self):
        serializer = ClientSerializer(
            data={
                "name": "Juan Perez",
                "company": "ACME",
                "email": "juan@empresa.com",
                "phone": "12345678",
                "status": "prospect",
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_rejects_phone_without_8_digits(self):
        serializer = ClientSerializer(
            data={
                "name": "Maria Lopez",
                "company": "ACME",
                "email": "maria@gmail.com",
                "phone": "12345",
                "status": "prospect",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone", serializer.errors)

    def test_accepts_valid_client_payload(self):
        serializer = ClientSerializer(
            data={
                "name": "Carlos Soto",
                "company": "ACME",
                "email": "CARLOS@OUTLOOK.COM",
                "phone": "1234-5678",
                "status": "prospect",
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["email"], "carlos@outlook.com")


class LeadConvertActionTests(APITestCase):
    def setUp(self):
        self.lead = Lead.objects.create(
            name="Lead Uno",
            email="leaduno@gmail.com",
            phone="12345678",
            message="Interesado en un producto",
        )

    @patch("clients.views.send_mail")
    def test_convert_marks_lead_and_creates_client(self, _send_mail_mock):
        url = reverse("lead-convert", args=[self.lead.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lead.refresh_from_db()
        self.assertTrue(self.lead.converted)
        self.assertTrue(Client.objects.filter(email="leaduno@gmail.com").exists())

    @patch("clients.views.send_mail")
    def test_convert_is_idempotent_for_already_converted_lead(self, _send_mail_mock):
        first_url = reverse("lead-convert", args=[self.lead.id])
        first_response = self.client.post(first_url)
        self.assertEqual(first_response.status_code, status.HTTP_200_OK)

        second_response = self.client.post(first_url)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Client.objects.filter(email="leaduno@gmail.com").count(), 1)

    @patch("clients.views.send_mail")
    def test_convert_reuses_existing_client_with_same_email(self, _send_mail_mock):
        Client.objects.create(
            name="Cliente Existente",
            company="ACME",
            email="leadduplicado@gmail.com",
            phone="87654321",
            status="prospect",
        )
        duplicate_lead = Lead.objects.create(
            name="Lead Duplicado",
            email="LEADDUPLICADO@GMAIL.COM",
            phone="11112222",
            message="Mensaje",
        )

        url = reverse("lead-convert", args=[duplicate_lead.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        duplicate_lead.refresh_from_db()
        self.assertTrue(duplicate_lead.converted)
        self.assertEqual(Client.objects.filter(email="leadduplicado@gmail.com").count(), 1)

    @patch("clients.views.send_mail")
    def test_convert_returns_400_when_lead_phone_is_empty(self, _send_mail_mock):
        no_phone_lead = Lead.objects.create(
            name="Lead Sin Telefono",
            email="sintelefono@icloud.com",
            phone="",
            message="Mensaje",
        )
        url = reverse("lead-convert", args=[no_phone_lead.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)
        no_phone_lead.refresh_from_db()
        self.assertFalse(no_phone_lead.converted)
        self.assertFalse(Client.objects.filter(email="sintelefono@icloud.com").exists())
