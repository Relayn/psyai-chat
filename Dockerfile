# Используем официальный образ Python
FROM python:3.13-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем системные зависимости
# build-essential и libpq-dev нужны для сборки psycopg2
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Устанавливаем Poetry
RUN pip install poetry

# Копируем файлы с зависимостями
# Мы копируем их отдельно, чтобы Docker мог кэшировать этот слой
COPY poetry.lock pyproject.toml /app/

# Устанавливаем зависимости проекта, не устанавливая сам проект
# и не создавая виртуальное окружение внутри Docker
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

# Копируем весь остальной код проекта в контейнер
COPY . /app/

# Открываем порт, который будет использовать Django
EXPOSE 8000

# Команда для запуска приложения (пока что просто для примера)
# Мы будем переопределять ее в docker-compose.yml
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]