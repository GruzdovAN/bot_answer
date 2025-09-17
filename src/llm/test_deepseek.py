#!/usr/bin/env python3
"""
Тестовый файл для проверки функции обработки сообщений из Telegram каналов
"""

import logging
from deepseek import process_telegram_message

# Настройка логирования для тестов
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_casting_message_processing():
    """Тест обработки сообщения о кастинге"""
    
    # Тестовое сообщение о кастинге
    casting_message = """
Москва!

Кастинг для проекта онлайн игра. 

ДАТЫ:
21 сентября  -примерка 
22 и 23 сентября - смена в один из дней (Москва)

ГОНОРАР (+ налог, постоплата на СЗ/ИП в течение 30 раб дней): 
Второй  план -  70.000-20%

ОПИСАНИЕ ГЕРОЕВ (важно быть готовыми записать самопробы оперативно):
1) трое футболистов около 30 лет, спортивное телесложение. 
2) Мужчина с подарками в новогоднюю ночь (отец семейства)  35-45 лет 
3) Мужчины hr менеджер 35-45 и Мужчина кандидат на собеседовании 25-35
4) Мужчина  учитель (истории?) в возрасте +50 
5) Автолюбитель на паркинге женщина, 35-40 лет. Наличие прав обязательно 
6) Слесарь с завода мужик работяга 30-50 лет

ПРАВА:
РФ, 2 месяца - ТВ, интернет,  DOOH, архив

КОНКУРЕНТЫ: 
Ценим незасвеченность
"""
    
    logger.info("=== НАЧАЛО ТЕСТА ОБРАБОТКИ СООБЩЕНИЯ ===")
    
    # Обрабатываем сообщение
    result = process_telegram_message(casting_message)
    
    # Выводим результат в удобном формате
    logger.info("=== РЕЗУЛЬТАТ ОБРАБОТКИ СООБЩЕНИЯ ===")
    logger.info(f"Успешно: {result['success']}")
    logger.info(f"Модель: {result['model_used']}")
    logger.info(f"Время: {result['timestamp']}")
    
    if result['success'] and result['extracted_data']:
        logger.info("Извлеченные данные:")
        for key, value in result['extracted_data'].items():
            if isinstance(value, list):
                logger.info(f"  {key}: {len(value)} элементов")
                for i, item in enumerate(value):
                    logger.info(f"    [{i+1}] {item}")
            else:
                logger.info(f"  {key}: {value}")
    
    if result['cost_info']:
        logger.info(f"Стоимость: ${result['cost_info'].get('total_cost_usd', 'N/A')}")
    
    if result['error']:
        logger.error(f"Ошибка: {result['error']}")
    
    # Возвращаем полный JSON для дальнейшего использования
    logger.info("Полный JSON ответ готов для использования в Telegram боте")
    
    return result

def test_short_message():
    """Тест обработки короткого сообщения"""
    
    short_message = "Кастинг на мужчину 30-40 лет для рекламы"
    
    logger.info("=== ТЕСТ КОРОТКОГО СООБЩЕНИЯ ===")
    result = process_telegram_message(short_message)
    
    logger.info(f"Результат: {result['success']}")
    if result['extracted_data']:
        logger.info(f"Тип сообщения: {result['extracted_data'].get('message_type', 'N/A')}")
    
    return result

def test_invalid_message():
    """Тест обработки некорректного сообщения"""
    
    invalid_message = "Это просто обычное сообщение, не связанное с кастингом"
    
    logger.info("=== ТЕСТ НЕКОРРЕКТНОГО СООБЩЕНИЯ ===")
    result = process_telegram_message(invalid_message)
    
    logger.info(f"Результат: {result['success']}")
    if result['error']:
        logger.info(f"Ошибка: {result['error']}")
    
    return result

if __name__ == "__main__":
    try:
        # Запускаем все тесты
        logger.info("Запуск тестов обработки сообщений...")
        
        # Тест 1: Полное сообщение о кастинге
        result1 = test_casting_message_processing()
        
        # Тест 2: Короткое сообщение
        result2 = test_short_message()
        
        # Тест 3: Некорректное сообщение
        result3 = test_invalid_message()
        
        logger.info("=== ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ ===")
        
    except Exception as e:
        logger.error(f"Ошибка при выполнении тестов: {e}")
