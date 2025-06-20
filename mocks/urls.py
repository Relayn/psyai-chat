from django.urls import path

from . import views

app_name = "mocks"

urlpatterns = [
    path("image-analysis/", views.upload_image_view, name="image_analysis"),
    path("payment/", views.mock_payment_view, name="mock_payment"),
]