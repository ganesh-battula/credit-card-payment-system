from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from payments.views import (
    RegisterView, LogoutView,
    CardListCreateView, CardDeleteView,
    TransactionListView, ExportTransactionsCSVView
)

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # MODULE 1: AUTHENTICATION
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/login/", TokenObtainPairView.as_view(), name="login"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/logout/", LogoutView.as_view(), name="logout"),

    # MODULE 2: CARD MANAGEMENT
    path("api/cards/", CardListCreateView.as_view(), name="card_list_create"),
    path("api/cards/<int:pk>/", CardDeleteView.as_view(), name="card_delete"),

    # MODULE 4: TRANSACTION MANAGEMENT & EXPORT
    path("api/transactions/", TransactionListView.as_view(), name="transactions_history"),
    path("api/admin/export-csv/", ExportTransactionsCSVView.as_view(), name="export_csv"),
]