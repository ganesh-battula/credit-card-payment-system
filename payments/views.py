import csv
from django.http import HttpResponse
from rest_framework import generics, permissions, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Card, Transaction
from .serializers import UserRegistrationSerializer, CardSerializer, TransactionSerializer


# MODULE 1: USER AUTHENTICATION
class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)


# MODULE 2: CARD MANAGEMENT
class CardListCreateView(generics.ListCreateAPIView):
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CardDeleteView(generics.DestroyAPIView):
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)


# MODULE 4: TRANSACTION MANAGEMENT & CSV
class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        "status": ["exact"],
        "amount": ["gte", "lte"],
        "created_at": ["gte", "lte", "date"],
    }
    ordering = ["-created_at"]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class ExportTransactionsCSVView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="transactions_report.csv"'

        writer = csv.writer(response)
        writer.writerow(["Transaction ID", "User", "Amount", "Currency", "Status", "Failure Reason", "Timestamp"])

        transactions = Transaction.objects.select_related("user").all()
        for tx in transactions:
            writer.writerow([
                tx.transaction_id,
                tx.user.username,
                tx.amount,
                tx.currency,
                tx.status,
                tx.failure_reason or "N/A",
                tx.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ])
        return response