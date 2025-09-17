# Модуль LLM

Универсальный модуль для работы с различными LLM (Large Language Models) провайдерами без привязки к конкретной предметной области.

## Возможности

- **Множественные провайдеры**: OpenAI, GigaChat, DeepSeek, OpenRouter
- **Универсальный интерфейс**: Единый API для всех провайдеров
- **Гибкие промпты**: Поддержка шаблонов с условными блоками
- **Повторные попытки**: Автоматические ретраи с экспоненциальной задержкой
- **Статистика**: Сбор метрик использования и производительности
- **Подсчет токенов**: Приблизительный подсчет токенов и стоимости
- **Пакетная обработка**: Обработка множественных запросов

## Структура модуля

```
src/llm/
├── __init__.py          # Основные экспорты
├── base.py              # Базовые классы
├── providers.py         # Провайдеры LLM
├── prompt_builder.py    # Строитель промптов
├── pipeline.py          # Основной пайплайн
├── utils.py             # Утилиты
├── example.py           # Примеры использования
└── README.md            # Документация
```

## Быстрый старт

### Базовое использование

```python
from src.llm import LLMPipeline, LLMRequest, OpenAIProvider

# Создаем провайдер
provider = OpenAIProvider(api_key="your-api-key")

# Создаем пайплайн
pipeline = LLMPipeline(provider)

# Создаем запрос
request = LLMRequest(
    request_id="example_1",
    system_prompt="Ты полезный AI-ассистент.",
    user_prompt="Объясни, что такое машинное обучение.",
    is_json=False
)

# Обрабатываем запрос
result = pipeline.process_request(request)

if result.status == 'success':
    print(result.response.content)
else:
    print(f"Ошибка: {result.error_message}")
```

### Пакетная обработка

```python
# Создаем несколько запросов
requests = [
    LLMRequest(
        request_id=f"batch_{i}",
        system_prompt="Ты помощник по математике.",
        user_prompt=f"Реши уравнение: {i}x + {i+1} = {i*2 + 1}",
        is_json=False
    )
    for i in range(1, 4)
]

# Обрабатываем пакет
results = pipeline.process_batch(requests)

for result in results:
    print(f"Запрос {result.request_id}: {result.status}")
```

## Провайдеры

### OpenAI

```python
from src.llm import OpenAIProvider

provider = OpenAIProvider(
    api_key="your-api-key",
    model="gpt-4o-mini",
    temperature=0.7,
    proxy_url="http://proxy:8080"  # Опционально
)
```

### GigaChat

```python
from src.llm import GigaChatProvider

provider = GigaChatProvider(
    credentials="your-credentials",
    model="GigaChat",
    temperature=0.7
)
```

### DeepSeek

```python
from src.llm import DeepSeekProvider

provider = DeepSeekProvider(
    api_key="your-api-key",
    model="deepseek-chat",
    temperature=0.7
)
```

### OpenRouter

```python
from src.llm import OpenRouterProvider

provider = OpenRouterProvider(
    api_key="your-api-key",
    model="anthropic/claude-3-haiku",
    temperature=0.7
)
```

## Строитель промптов

### Базовый шаблон

```python
from src.llm import PromptBuilder, PromptParameters

builder = PromptBuilder()

parameters = PromptParameters(
    system_prompt="Ты эксперт по программированию.",
    user_prompt="Напиши функцию для сортировки массива.",
    context="Используй Python",
    additional_data={"style": "функциональный"}
)

prompt = builder.build_prompt(parameters)
```

### Кастомный шаблон

```python
custom_template = """
Ты {{ROLE}}.

{{#if CONTEXT}}
Контекст: {{CONTEXT}}
{{/if}}

Задача: {{USER_PROMPT}}

{{#if ADDITIONAL_DATA}}
Дополнительные требования:
{{ADDITIONAL_DATA}}
{{/if}}
"""

builder.set_template(custom_template)
```

## Статистика и мониторинг

```python
# Получить статистику
stats = pipeline.get_statistics()
print(f"Всего запросов: {stats['total_requests']}")
print(f"Процент успеха: {stats['success_rate']:.1f}%")
print(f"Средняя стоимость: ${stats['average_cost_per_request']:.4f}")

# Сбросить статистику
pipeline.reset_statistics()
```

## Настройка повторных попыток

```python
# Настроить параметры ретраев
pipeline.set_retry_config(
    max_retries=5,
    base_delay=2.0,
    max_delay=30.0
)
```

## Структуры данных

### LLMRequest

```python
@dataclass
class LLMRequest:
    request_id: str
    system_prompt: str
    user_prompt: str
    context: str = ""
    additional_data: Optional[Dict[str, Any]] = None
    is_json: bool = False
    max_retries: int = 3
```

### LLMResult

```python
@dataclass
class LLMResult:
    request_id: str
    response: Optional[LLMResponse]
    input_tokens: int
    output_tokens: int
    total_cost: float
    retry_count: int
    response_time: float
    status: str  # 'success' или 'error'
    error_message: Optional[str] = None
    timestamp: float = 0.0
```

### LLMResponse

```python
class LLMResponse(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None
```

## Утилиты

### Подсчет токенов

```python
from src.llm import TokenCounter

counter = TokenCounter()
tokens = counter.count_tokens("Привет, мир!")
print(f"Токенов: {tokens}")
```

### Расчет стоимости

```python
from src.llm import CostCalculator

calculator = CostCalculator()
cost = calculator.calculate_cost("gpt-4o-mini", 100, 50)
print(f"Стоимость: ${cost:.4f}")
```

## Примеры

Запустите файл `example.py` для просмотра полных примеров использования:

```bash
python src/llm/example.py
```

## Требования

- Python 3.8+
- openai
- httpx
- pydantic

## Установка зависимостей

```bash
pip install openai httpx pydantic
```

## Примечания

- Некоторые провайдеры (GigaChat) требуют дополнительных библиотек
- Подсчет токенов является приблизительным
- Цены на модели могут изменяться
- Для продакшена рекомендуется добавить более точный подсчет токенов с помощью tiktoken
