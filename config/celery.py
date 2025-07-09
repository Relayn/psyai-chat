import os

from celery import Celery

# Устанавливаем переменную окружения, чтобы Celery знал,
# где найти настройки нашего Django-проекта.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Создаем экземпляр приложения Celery
app = Celery("config")

# Используем пространство имен 'CELERY' для настроек.
# Это значит, что все настройки Celery в settings.py должны начинаться
# с префикса CELERY_, например, CELERY_BROKER_URL.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Эта строка автоматически находит и загружает задачи (tasks.py)
# из всех зарегистрированных приложений Django.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Пример задачи для отладки."""
    print(f"Request: {self.request!r}")
