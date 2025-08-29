# --- СТАДИЯ 1: Сборщик зависимостей ---
# На этой стадии мы используем Poetry только для генерации requirements.txt.
# Используем полный образ, чтобы у Poetry точно были все инструменты.
FROM python:3.13 AS builder

# Устанавливаем конкретную современную версию Poetry, чтобы избежать проблем со старыми командами
RUN pip install poetry==1.8.2

WORKDIR /app
COPY poetry.lock pyproject.toml ./

# Генерируем requirements.txt для основного приложения (app, worker)
# ИСПОЛЬЗУЕМ `python -m poetry`, чтобы гарантированно вызвать нужную версию
RUN python -m poetry export -f requirements.txt --output requirements.txt --without dev

# Генерируем requirements.txt для Flower
# ИСПОЛЬЗУЕМ `python -m poetry`, чтобы гарантированно вызвать нужную версию
RUN python -m poetry export -f requirements.txt --output flower-requirements.txt --with monitoring --without dev


# --- СТАДИЯ 2: Финальный образ для App и Worker ---
# Возвращаемся к slim-образу для экономии места
FROM python:3.13-slim AS app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Устанавливаем только необходимые для работы системные зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Копируем сгенерированный requirements.txt из сборщика
COPY --from=builder /app/requirements.txt .

# Устанавливаем зависимости через pip, что быстрее и надежнее в Docker
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем непривилегированного пользователя для безопасности
RUN addgroup --system appuser && \
    adduser --system --ingroup appuser appuser && \
    mkdir -p /app/media /app/staticfiles && \
    chown -R appuser:appuser /app

USER appuser
EXPOSE 8000


# --- СТАДИЯ 3: Финальный образ для Flower ---
FROM python:3.13-slim AS flower

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Копируем сгенерированный requirements.txt для Flower
COPY --from=builder /app/flower-requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r flower-requirements.txt

# Копируем код приложения
COPY . .

# Создаем пользователя
RUN addgroup --system appuser && \
    adduser --system --ingroup appuser appuser && \
    chown -R appuser:appuser /app

USER appuser
EXPOSE 5555
