# Используем официальный образ Python
FROM python:3.13-slim

# Устанавливаем переменные окружения, чтобы избежать лишних логов и проблем с буферизацией
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию
WORKDIR /app

# --- Оптимизированный блок установки зависимостей ---
# Объединяем все команды в один RUN, чтобы создать единый слой.
# 1. Обновляем списки пакетов.
# 2. Устанавливаем системные зависимости, необходимые для сборки (build-essential) и работы (libpq-dev).
# 3. Устанавливаем Poetry.
# 4. Очищаем кэш apt, чтобы уменьшить размер итогового образа.
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev && \
    pip install poetry && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копируем только файлы с зависимостями.
# Это позволяет Docker кэшировать этот слой. Если pyproject.toml и poetry.lock не менялись,
# Docker не будет переустанавливать зависимости при каждой сборке.
COPY poetry.lock pyproject.toml /app/

# Устанавливаем зависимости проекта с помощью Poetry.
# --no-root: не устанавливать сам проект как пакет.
# virtualenvs.create false: устанавливать зависимости в системный python, а не в .venv.
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

# Копируем весь остальной код проекта в контейнер.
# Этот слой будет пересобираться только при изменении кода.
COPY . /app/

# --- Оптимизированный блок создания пользователя и прав доступа ---
# Объединяем все команды в один RUN для создания одного слоя.
# 1. Создаем системную группу и пользователя без домашней директории.
# 2. Создаем папки для медиа и статики.
# 3. Меняем владельца всех файлов в /app на нашего непривилегированного пользователя.
RUN addgroup --system appuser && \
    adduser --system --ingroup appuser appuser && \
    mkdir -p /app/media /app/staticfiles && \
    chown -R appuser:appuser /app

# Переключаемся на непривилегированного пользователя для повышения безопасности.
# Все последующие команды будут выполняться от его имени.
USER appuser

# Открываем порт, который будет использовать Django
EXPOSE 8000

# Команда для запуска приложения
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
