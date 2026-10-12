from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from payments.models import Card

User = get_user_model()


class PaymentSystemTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="Password123!"
        )

    def test_user_registration(self):
        response = self.client.post("/api/auth/register/", {
            "username": "newuser",
            "email": "new@example.com",
            "password": "Password123!"
        })
        self.assertEqual(response.status_code, 201)

    def test_card_masking_security(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/cards/", {
            "card_holder_name": "Test User",
            "card_number": "4111111111114242",
            "cvv": "123",
            "card_type": "CREDIT",
            "expiry_month": 12,
            "expiry_year": 2028
        })
        self.assertEqual(response.status_code, 201)
        card = Card.objects.first()
        self.assertEqual(card.last_4_digits, "4242")
        self.assertTrue(card.masked_card_number.startswith("************"))
        self.assertNotIn("cvv", response.data)