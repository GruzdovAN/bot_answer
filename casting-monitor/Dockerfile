FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY src/ ./src/
COPY scripts/ ./scripts/

# Создание директорий для данных
RUN mkdir -p /app/sessions /app/logs

# Установка прав на выполнение скриптов
RUN chmod +x scripts/*.sh

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Точка входа
ENTRYPOINT ["./scripts/entrypoint.sh"]

# Команда по умолчанию
CMD ["python", "src/main.py"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD ./scripts/healthcheck.sh
