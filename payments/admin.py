from datetime import date
from django.contrib import admin
from django.db.models import Sum, Count, Q
from django.utils.html import format_html
from .models import User, Card, Transaction, AdminLog


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "is_staff", "is_active", "date_joined")
    search_fields = ("username", "email")


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "masked_card_number", "card_type", "expiry_month", "expiry_year", "created_at")
    list_filter = ("card_type",)
    search_fields = ("user__username", "last_4_digits")
    readonly_fields = ("masked_card_number", "last_4_digits")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "user", "amount", "currency", "colored_status", "created_at")
    list_filter = ("status", "currency", "created_at")
    search_fields = ("transaction_id", "user__username")
    readonly_fields = ("transaction_id", "created_at", "updated_at")

    def colored_status(self, obj):
        colors = {"SUCCESS": "green", "PENDING": "orange", "FAILED": "red"}
        return format_html(
            f'<b style="color: {colors.get(obj.status, "black")}">{obj.status}</b>'
        )
    colored_status.short_description = "Status"

    def changelist_view(self, request, extra_context=None):
        today = date.today()
        summary = Transaction.objects.filter(created_at__date=today).aggregate(
            total_count=Count("id"),
            total_volume=Sum("amount"),
            success_count=Count("id", filter=Q(status="SUCCESS")),
            failed_count=Count("id", filter=Q(status="FAILED")),
        )
        extra_context = extra_context or {}
        extra_context["daily_summary"] = summary
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ("admin_user", "action", "timestamp")
    readonly_fields = ("admin_user", "action", "details", "timestamp")