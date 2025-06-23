from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'status', 'yookassa_payment_id', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'yookassa_payment_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')