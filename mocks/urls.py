from django.urls import path

from . import views

app_name = "mocks"

urlpatterns = [
    path("payment/", views.mock_payment_view, name="mock_payment"),
]