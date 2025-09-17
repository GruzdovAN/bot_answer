# Анализ существующих модулей для работы с ClickHouse

## 📋 Найденные модули

### 1. **`src/database/clickhouse_client.py`** - Основной клиент ClickHouse

**Функциональность:**
- Подключение к ClickHouse через HTTP API
- Методы для вставки данных в различные таблицы
- Обработка ошибок и логирование

**Ключевые методы:**
- `insert_messages()` - вставка общих сообщений Telegram
- `insert_castings_messages()` - вставка сообщений о кастингах
- `insert_channels_info()` - вставка информации о каналах
- `insert_all_channels()` - вставка всех каналов

**Использование в Docker контейнере:**
- Будет использован как базовый класс
- Добавлен метод `update_llm_analysis()` для обновления LLM результатов

### 2. **`config/database_config.py`** - Конфигурация базы данных

**Содержит:**
- Настройки подключения к ClickHouse
- Схемы таблиц
- SQL для создания таблиц

**Таблицы:**
- `telegram_messages` - общие сообщения
- `castings_messages` - сообщения о кастингах (основная для нашего проекта)
- `channels_info` - информация о каналах

### 3. **`scripts/read_castings_folder.py`** - Читатель кастинговых каналов

**Функциональность:**
- Чтение каналов из папки @castings в Telegram
- Парсинг сообщений о кастингах
- Сохранение в ClickHouse
- Обновление конфигурации каналов

**Класс `CastingsFolderReader`:**
- Автоматический выбор лучшей сессии Telegram
- Пакетная обработка сообщений
- Интеграция с ClickHouse
- Логирование операций

### 4. **`src/core/universal_scraper.py`** - Универсальный скрапер

**Функциональность:**
- Сбор данных со всех активных каналов
- Парсинг сообщений
- Сохранение в ClickHouse

**Класс `UniversalScraper`:**
- Управление каналами
- Парсинг сообщений
- Интеграция с ClickHouse

### 5. **`src/llm/deepseek.py`** - LLM обработчик

**Функциональность:**
- Обработка сообщений через DeepSeek API
- Извлечение структурированных данных о кастингах
- Расчет стоимости запросов
- Логирование операций

**Ключевая функция:**
- `process_telegram_message()` - основная функция обработки

## 🔧 Модификации для Docker контейнера

### 1. Расширение `clickhouse_client.py`

**Добавить метод:**
```python
def update_llm_analysis(self, message_id: int, llm_result: dict):
    """Обновление записи с результатом LLM анализа"""
    llm_json = json.dumps(llm_result, ensure_ascii=False)
    
    query = f"""
    ALTER TABLE {self.database}.castings_messages 
    UPDATE llm_analysis = '{llm_json}'
    WHERE message_id = {message_id}
    """
    
    response = requests.post(
        self.base_url,
        data=query,
        auth=self.auth,
        params={'database': self.database}
    )
    
    if response.status_code != 200:
        raise Exception(f"ClickHouse error: {response.text}")
```

### 2. Модификация схемы таблицы `castings_messages`

**Добавить поле:**
```sql
ALTER TABLE castings_messages 
ADD COLUMN llm_analysis JSON DEFAULT '{}'
```

### 3. Использование существующих компонентов

**В Docker контейнере будут использованы:**
- `src/database/clickhouse_client.py` - для работы с БД
- `src/llm/deepseek.py` - для LLM обработки
- `config/database_config.py` - для конфигурации БД
- `config/castings_channels.py` - для списка каналов

## 📊 Схема интеграции

```
Docker Container
├── CastingMonitor (новый)
│   ├── TelegramClient (Telethon)
│   ├── MessageProcessor (новый)
│   │   ├── ClickHouseClient (существующий)
│   │   └── LLMClient (обертка над deepseek.py)
│   └── Config (существующий)
└── Logging & Monitoring (новый)
```

## 🚀 Преимущества использования существующих модулей

1. **Переиспользование кода** - не нужно переписывать логику работы с ClickHouse
2. **Проверенная функциональность** - модули уже протестированы
3. **Единообразие** - использование тех же подходов и конфигураций
4. **Простота поддержки** - изменения в одном месте

## 🔄 Процесс интеграции

1. **Импорт существующих модулей** в Docker контейнер
2. **Создание оберток** для асинхронной работы
3. **Добавление новых методов** для обновления LLM результатов
4. **Настройка конфигурации** для Docker окружения
5. **Тестирование интеграции** с существующей системой

## 📝 Заключение

Существующие модули предоставляют отличную основу для создания Docker контейнера. Основная работа будет заключаться в:

1. Создании мониторинга в реальном времени
2. Интеграции LLM обработки с сохранением в БД
3. Добавлении поля `llm_analysis` в таблицу
4. Настройке Docker окружения

Все необходимые компоненты уже существуют и могут быть переиспользованы с минимальными модификациями.
