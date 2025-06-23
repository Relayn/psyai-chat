from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("create/", views.create_payment_view, name="create_payment"),
    path("webhook/", views.yookassa_webhook_view, name="yookassa_webhook"),
]