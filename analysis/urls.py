from django.urls import path
from . import views

app_name = "analysis"

urlpatterns = [
    path("upload/", views.upload_image_view, name="upload_image"),
    path("result/<int:result_id>/", views.analysis_result_view, name="analysis_result"),
    path("api/status/<int:result_id>/", views.get_analysis_status_view, name="get_analysis_status"),
]