# Быстрый старт с модулем LLM

## Установка зависимостей

```bash
pip install openai httpx pydantic
```

## Простейший пример

```python
from src.llm import LLMPipeline, LLMRequest, GigaChatProvider

# 1. Создаем провайдер
provider = GigaChatProvider(credentials="your-credentials")

# 2. Создаем пайплайн
pipeline = LLMPipeline(provider)

# 3. Создаем запрос
request = LLMRequest(
    request_id="my_request",
    system_prompt="Ты полезный ассистент.",
    user_prompt="Привет! Как дела?",
    is_json=False
)

# 4. Обрабатываем запрос
result = pipeline.process_request(request)

# 5. Получаем результат
if result.status == 'success':
    print(result.response.content)
else:
    print(f"Ошибка: {result.error_message}")
```

## Доступные провайдеры

- **OpenAI**: `OpenAIProvider(api_key="your-key")`
- **GigaChat**: `GigaChatProvider(credentials="your-credentials")`
- **DeepSeek**: `DeepSeekProvider(api_key="your-key")`
- **OpenRouter**: `OpenRouterProvider(api_key="your-key")`

## Пакетная обработка

```python
requests = [
    LLMRequest(
        request_id=f"batch_{i}",
        system_prompt="Ты помощник.",
        user_prompt=f"Вопрос номер {i}",
        is_json=False
    )
    for i in range(1, 4)
]

results = pipeline.process_batch(requests)
```

## Статистика

```python
stats = pipeline.get_statistics()
print(f"Успешных запросов: {stats['successful_requests']}")
print(f"Процент успеха: {stats['success_rate']:.1f}%")
```

## Запуск примеров

```bash
# Базовые примеры
python src/llm/example.py

# Полная демонстрация
python src/llm/demo.py

# Тесты
python src/llm/test_basic.py
```

## Документация

Полная документация доступна в файле `README.md`.
