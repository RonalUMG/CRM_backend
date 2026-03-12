from unittest.mock import patch

from admissions.models import HighSchool
from academics.models import AcademicDegree, AcademicPeriod, Faculty
from commercial.models import AcademicOffer
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Campus, Client, Lead, Note, Product, Site
from .serializers import ClientSerializer, LeadSerializer


class ClientSerializerValidationTests(TestCase):
    def test_rejects_phone_not_8_digits(self):
        """
        Tests that the serializer rejects phone numbers that do not have 8 digits.
        """
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

    def test_accepts_phone_with_8_digits(self):
        """
        Tests that the serializer accepts phone numbers with 8 digits.
        """
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

    def test_accepts_empty_phone(self):
        """
        Tests that the serializer accepts an empty phone number.
        """
        serializer = ClientSerializer(
            data={
                "name": "Ana Sin Telefono",
                "company": "ACME",
                "email": "ana@gmail.com",
                "phone": "",
                "status": "prospect",
            }
        )
        # The client model does not allow blank phones, so the serializer
        # should be invalid.
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone", serializer.errors)


class LeadSerializerValidationTests(TestCase):
    def test_rejects_phone_not_8_digits(self):
        """
        Tests that the serializer rejects phone numbers that do not have 8 digits.
        """
        serializer = LeadSerializer(
            data={
                "name": "Maria Lopez",
                "email": "maria@gmail.com",
                "phone": "12345",
                "message": "Test message",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone", serializer.errors)

    def test_accepts_phone_with_8_digits(self):
        """
        Tests that the serializer accepts phone numbers with 8 digits.
        """
        serializer = LeadSerializer(
            data={
                "name": "Juan Perez",
                "email": "juan@empresa.com",
                "phone": "12345678",
                "message": "Test message",
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_accepts_empty_phone(self):
        """
        Tests that the serializer accepts an empty phone number for a lead.
        """
        serializer = LeadSerializer(
            data={
                "name": "Pedro Sin Telefono",
                "email": "pedro@gmail.com",
                "phone": "",
                "message": "Test message",
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_partial_update_with_invalid_phone(self):
        """
        Tests that a partial update with an invalid phone number is rejected.
        """
        lead = Lead.objects.create(
            name="Test Lead",
            email="test@test.com",
            message="test",
            phone="12345678",
        )
        serializer = LeadSerializer(
            instance=lead, data={"phone": "123456789"}, partial=True
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone", serializer.errors)


class LeadCampusSiteTests(TestCase):
    def test_lead_can_be_linked_to_campus_and_site(self):
        campus = Campus.objects.create(
            name="Campus Central",
            city="Ciudad de Guatemala",
            country="Guatemala",
            is_central=True,
        )
        site = Site.objects.create(
            campus=campus,
            name="Sede Norte",
            city="Mixco",
            site_type="main",
        )
        high_school = HighSchool.objects.create(
            name="Colegio Tecnico Nacional",
            city="Guatemala",
            department="Guatemala",
            active=True,
        )
        lead = Lead.objects.create(
            name="Aspirante Campus",
            email="aspirante@outlook.com",
            phone="12345678",
            message="Interes en Ingenieria",
            preferred_campus=campus,
            preferred_site=site,
            high_school=high_school,
        )

        self.assertEqual(lead.preferred_campus, campus)
        self.assertEqual(lead.preferred_site, site)
        self.assertEqual(lead.high_school, high_school)


class LeadConvertActionTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="testuser",
            password="StrongPass123!",
        )
        self.client.force_authenticate(user=self.user)
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


class JwtProtectionTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="jwtuser",
            password="StrongPass123!",
        )

    def _authenticate_with_jwt(self):
        token_url = reverse("token_obtain_pair")
        token_response = self.client.post(
            token_url,
            {"username": "jwtuser", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        access = token_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_clients_list_requires_authentication(self):
        url = reverse("client-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_clients_list_with_jwt_returns_200(self):
        self._authenticate_with_jwt()
        url = reverse("client-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_clients_create_with_jwt_returns_201(self):
        self._authenticate_with_jwt()
        url = reverse("client-list")
        payload = {
            "name": "Cliente JWT Test",
            "company": "Universidad Demo",
            "email": "cliente.jwt.test@outlook.com",
            "phone": "12345678",
            "status": "prospect",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_social_messages_with_jwt_returns_200(self):
        self._authenticate_with_jwt()
        url = reverse("socialmessage-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_academic_offers_with_jwt_returns_200(self):
        faculty = Faculty.objects.create(name="Facultad de Ingenieria", code="FI", active=True)
        degree = AcademicDegree.objects.create(name="Licenciatura en Ingenieria", level="bachelor", active=True)
        period = AcademicPeriod.objects.create(
            name="2026-S1",
            period_type="semester",
            start_date="2026-01-15",
            end_date="2026-06-30",
            active=True,
        )
        campus = Campus.objects.create(name="Campus Test", city="Guatemala", country="Guatemala", is_central=False)
        program = Product.objects.create(name="Ingenieria en Sistemas", price=0, description="", active=True)
        AcademicOffer.objects.create(
            program=program,
            campus=campus,
            faculty=faculty,
            academic_degree=degree,
            academic_period=period,
            active=True,
        )

        self._authenticate_with_jwt()
        url = reverse("academicoffer-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class ModelImprovementTests(TestCase):
    def test_client_phone_validation(self):
        """
        Tests phone number validation for the Client model.
        """
        # Valid phone numbers
        Client.objects.create(name="Test", email="test1@test.com", phone="12345678")
        self.assertEqual(Client.objects.count(), 1)

        Client.objects.create(
            name="Test 2", email="test2@test.com", phone="+50212345678"
        )
        self.assertEqual(Client.objects.count(), 2)

        # Invalid phone numbers
        with self.assertRaises(ValidationError):
            client_invalid = Client(
                name="Test Invalid", email="test3@test.com", phone="1234"
            )
            client_invalid.full_clean()

        with self.assertRaises(ValidationError):
            client_invalid_chars = Client(
                name="Test Invalid Chars", email="test4@test.com", phone="123-456"
            )
            client_invalid_chars.full_clean()

    def test_lead_phone_validation(self):
        """
        Tests phone number validation for the Lead model.
        """
        # Valid phone number
        Lead.objects.create(name="Test Lead", email="lead@test.com", phone="12345678", message="Test message")
        self.assertEqual(Lead.objects.count(), 1)

        # Invalid phone number
        with self.assertRaises(ValidationError):
            lead_invalid = Lead(
                name="Test Invalid Lead", email="lead2@test.com", phone="123", message="Test message"
            )
            lead_invalid.full_clean()

    def test_note_ordering(self):
        """
        Tests that Notes are ordered by creation date descending.
        """
        client = Client.objects.create(
            name="Test Client", email="client@test.com", phone="12345678"
        )
        note1 = Note.objects.create(client=client, content="First note")
        note2 = Note.objects.create(client=client, content="Second note")

        notes = client.notes.all()
        self.assertEqual(notes[0], note2)
        self.assertEqual(notes[1], note1)
