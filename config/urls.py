from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Подключаем все маршруты из нашего приложения users
    path("", include("users.urls")),
    # Подключаем все маршруты из нашего приложения chat
    path("", include("chat.urls")),
    path("payments/", include("payments.urls")),
    path("analysis/", include("analysis.urls")),
]

# --- Маршрутизация для медиафайлов в режиме разработки ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
