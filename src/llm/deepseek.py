import os
from dotenv import load_dotenv
import json
import logging
from openai import OpenAI
# Загружаем переменные окружения из файла .env
env_path = ".env"
load_dotenv(env_path)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

api_key = os.getenv('DEEPSEEK_API_KEY')

model_chat="deepseek-chat"
model_reasoner="deepseek-reasoner"
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)
# Простая функция для списка актеров
tools_casting = [
    {
        "type": "function",
        "function": {
            "name": "parse_casting_message",
            "strict": False,
            "description": "Извлечь информацию о кастинге. ВСЕГДА используй эту функцию для анализа сообщений о кастингах.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message_type": {
                        "type": "string",
                        "description": "Тип сообщения",
                        "enum": ["кастинг", "рекламное объявление", "прочее"]
                    },
                    "casting_type": {
                        "type": "string",
                        "description": "Тип кастинга",
                        "enum": ["кино", "сериал", "реклама", "театр", "прочее"]
                    },
                    "actors": {
                        "type": "array",
                        "description": "Список актеров",
                        "items": {
                            "type": "object",
                            "properties": {
                                "gender": {
                                    "type": "string",
                                    "description": "Пол актера",
                                    "enum": ["мужчина", "женщина"]
                                },
                                "age_range": {
                                    "type": "string",
                                    "description": "Возрастной диапазон актера"
                                },
                                "role_features": {
                                    "type": "string",
                                    "description": "Особенности роли (например: спортивное телосложение, наличие прав, профессия и т.д.)"
                                }
                            },
                            "required": ["gender", "age_range", "role_features"]
                        }
                    },
                    "has_target_woman": {
                        "type": "boolean",
                        "description": "Есть ли в списке актеров женщина в возрасте 30-45 лет"
                    }
                },
                "required": ["message_type", "casting_type", "actors", "has_target_woman"]
            }
        }
    }
]

logger.info("Простая функция для списка актеров создана")

# Функция для расчета стоимости сообщения
def calculate_message_cost(input_tokens, output_tokens, cache_hit=False):
    """
    Расчет стоимости сообщения для DeepSeek API
    
    Args:
        input_tokens: количество входных токенов
        output_tokens: количество выходных токенов
        cache_hit: True если кэш попал, False если промах
    
    Returns:
        dict: стоимость и детали расчета
    """
    # Цены за 1M токенов
    input_price_per_1m = 0.07 if cache_hit else 0.56  # USD
    output_price_per_1m = 1.68  # USD
    
    # Расчет стоимости
    input_cost = (input_tokens / 1_000_000) * input_price_per_1m
    output_cost = (output_tokens / 1_000_000) * output_price_per_1m
    total_cost = input_cost + output_cost
    
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cache_hit": cache_hit,
        "input_cost_usd": round(input_cost, 6),
        "output_cost_usd": round(output_cost, 6),
        "total_cost_usd": round(total_cost, 6),
    }

# Пример использования
example_cost = calculate_message_cost(1000, 500, cache_hit=False)
logger.info(f"Пример расчета стоимости: {example_cost}")

def process_telegram_message(message_text: str, model: str = "deepseek-chat") -> dict:
    """
    Обработка сообщения из Telegram канала для извлечения информации о кастинге
    
    Args:
        message_text: Текст сообщения из Telegram канала
        model: Модель для обработки (по умолчанию deepseek-chat)
    
    Returns:
        dict: Полный JSON ответ с результатами обработки
    """
    try:
        logger.info(f"Начинаем обработку сообщения длиной {len(message_text)} символов")
        
        # Подготавливаем сообщение для API
        messages = [{"role": "user", "content": f"ВЫЗОВИ ФУНКЦИЮ parse_casting_message для анализа этого сообщения о кастинге: {message_text}"}]
        
        # Отправляем запрос к API
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools_casting
        )
        
        message = response.choices[0].message
        
        # Формируем базовый ответ
        result = {
            "success": True,
            "message_type": "casting_analysis",
            "original_message": message_text,
            "model_used": model,
            "timestamp": None,  # Будет заполнено при вызове
            "extracted_data": None,
            "cost_info": None,
            "error": None
        }
        
        # Добавляем timestamp
        from datetime import datetime
        result["timestamp"] = datetime.now().isoformat()
        
        # Обрабатываем ответ модели
        if message.tool_calls:
            logger.info(f"Модель вызвала функцию: {message.tool_calls[0].function.name}")
            
            try:
                # Парсим аргументы функции
                params = json.loads(message.tool_calls[0].function.arguments)
                result["extracted_data"] = params
                logger.info("Данные успешно извлечены и структурированы")
                
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка парсинга JSON: {e}")
                result["error"] = f"Ошибка парсинга JSON: {e}"
                result["success"] = False
                
        else:
            logger.warning("Модель не вызвала функцию для анализа")
            result["error"] = "Модель не вызвала функцию для анализа"
            result["success"] = False
        
        # Добавляем информацию о стоимости
        if hasattr(response, 'usage') and response.usage:
            usage = response.usage
            cost_info = calculate_message_cost(
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                cache_hit=False
            )
            result["cost_info"] = cost_info
            logger.info(f"Стоимость обработки: ${cost_info['total_cost_usd']}")
        else:
            logger.warning("Информация о токенах недоступна")
            result["cost_info"] = {"error": "Информация о токенах недоступна"}
        
        logger.info("Обработка сообщения завершена успешно")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        return {
            "success": False,
            "message_type": "casting_analysis",
            "original_message": message_text,
            "model_used": model,
            "timestamp": datetime.now().isoformat() if 'datetime' in locals() else None,
            "extracted_data": None,
            "cost_info": None,
            "error": str(e)
        }

