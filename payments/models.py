from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)

    class Meta:
        db_table = "users"


class Card(models.Model):
    CARD_TYPES = (
        ("CREDIT", "Credit Card"),
        ("DEBIT", "Debit Card"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cards")
    card_holder_name = models.CharField(max_length=150)
    masked_card_number = models.CharField(max_length=20)
    last_4_digits = models.CharField(max_length=4)
    card_type = models.CharField(max_length=10, choices=CARD_TYPES, default="CREDIT")
    expiry_month = models.IntegerField()
    expiry_year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cards"

    def __str__(self):
        return f"{self.card_holder_name} ({self.masked_card_number})"


class Transaction(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    )
    transaction_id = models.CharField(max_length=64, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, related_name="transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="INR")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    failure_reason = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transactions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"


class AdminLog(models.Model):
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admin_logs"

    def __str__(self):
        return f"{self.action} at {self.timestamp}"