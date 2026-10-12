import re
from rest_framework import serializers
from .models import User, Card, Transaction


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"]
        )


class CardSerializer(serializers.ModelSerializer):
    card_number = serializers.CharField(write_only=True, min_length=13, max_length=19)
    cvv = serializers.CharField(write_only=True, min_length=3, max_length=4)

    class Meta:
        model = Card
        fields = (
            "id", "card_holder_name", "card_number", "cvv",
            "masked_card_number", "last_4_digits", "card_type",
            "expiry_month", "expiry_year", "created_at"
        )
        read_only_fields = ("masked_card_number", "last_4_digits", "created_at")

    def validate_card_number(self, value):
        cleaned = re.sub(r"\D", "", value)
        if len(cleaned) not in [15, 16]:
            raise serializers.ValidationError("Invalid card number length.")
        return cleaned

    def create(self, validated_data):
        raw_number = validated_data.pop("card_number")
        validated_data.pop("cvv")  # Never store CVV
        
        last_4 = raw_number[-4:]
        masked = ("*" * (len(raw_number) - 4)) + last_4

        return Card.objects.create(
            masked_card_number=masked,
            last_4_digits=last_4,
            **validated_data
        )


class TransactionSerializer(serializers.ModelSerializer):
    card_details = serializers.CharField(source="card.masked_card_number", read_only=True)

    class Meta:
        model = Transaction
        fields = (
            "transaction_id", "amount", "currency", "status",
            "failure_reason", "card_details", "created_at"
        )