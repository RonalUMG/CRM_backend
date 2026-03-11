from rest_framework import serializers

from admissions.models import HighSchool, SocialMessage
from commercial.models import AcademicOffer
from .models import Client, Lead, Note, Opportunity, Product


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "content", "created_at"]


class ClientSerializer(serializers.ModelSerializer):
    notes = NoteSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = ["id", "name", "company", "email", "phone", "status", "created_at", "notes"]
        read_only_fields = ["created_at", "notes"]

    def validate_email(self, value):
        return value.strip().lower()

    def validate_phone(self, value):
        digits = "".join(filter(str.isdigit, value))
        if len(digits) != 8:
            raise serializers.ValidationError("El telefono debe tener 8 digitos")
        return value

    def validate(self, data):
        status_value = data.get("status")
        phone_value = data.get("phone")
        if status_value == "inactive" and phone_value:
            raise serializers.ValidationError("Un cliente inactivo no debe tener telefono registrado.")
        return data


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = "__all__"


class HighSchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = HighSchool
        fields = "__all__"


class SocialMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMessage
        fields = "__all__"


class AcademicOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicOffer
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class OpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = "__all__"
