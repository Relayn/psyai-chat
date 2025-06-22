# Используем официальный образ Python
FROM python:3.13-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Создаем непривилегированного пользователя
RUN addgroup --system appuser && adduser --system --ingroup appuser appuser

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Устанавливаем Poetry
RUN pip install poetry

# Копируем файлы с зависимостями
COPY poetry.lock pyproject.toml /app/

# Устанавливаем зависимости проекта
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

# Копируем весь остальной код проекта в контейнер
COPY . /app/

# --- ИСПРАВЛЕНИЕ: Создаем папку для медиафайлов ---
# Причина: Создаем папку media и staticsfiles до смены пользователя,
# чтобы затем корректно назначить на них права.
RUN mkdir -p /app/media /app/staticfiles

# --- ИСПРАВЛЕНИЕ: Меняем владельца всех файлов, включая media ---
# Причина: Делаем нашего пользователя владельцем всех файлов в /app,
# включая только что созданную папку /media, чтобы он мог в нее писать.
RUN chown -R appuser:appuser /app

# Переключаемся на непривилегированного пользователя
USER appuser

# Открываем порт, который будет использовать Django
EXPOSE 8000

# Команда для запуска приложения
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]