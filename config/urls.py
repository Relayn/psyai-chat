from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Подключаем все маршруты из нашего приложения users
    path("", include("users.urls")),
    # Подключаем все маршруты из нашего приложения chat
    path("", include("chat.urls")),
]