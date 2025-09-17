#!/usr/bin/env python3
"""
Пример использования модуля LLM

Этот файл демонстрирует основные возможности модуля для работы с LLM
без привязки к конкретной предметной области.
"""

import os
import logging
from typing import Dict, Any

from .pipeline import LLMPipeline, LLMRequest
from .providers import OpenAIProvider, GigaChatProvider, DeepSeekProvider, OpenRouterProvider

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_openai_usage():
    """Пример использования с OpenAI"""
    print("\n" + "="*50)
    print("ПРИМЕР С OPENAI")
    print("="*50)
    
    # Создаем провайдер OpenAI
    api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
    provider = OpenAIProvider(api_key=api_key, model="gpt-4o-mini")
    
    # Создаем пайплайн
    pipeline = LLMPipeline(provider)
    
    # Создаем запрос
    request = LLMRequest(
        request_id="example_1",
        system_prompt="Ты полезный AI-ассистент. Отвечай кратко и по делу.",
        user_prompt="Объясни, что такое машинное обучение в двух предложениях.",
        context="",
        additional_data={"language": "русский"},
        is_json=False
    )
    
    # Обрабатываем запрос
    result = pipeline.process_request(request)
    
    # Выводим результат
    print(f"Статус: {result.status}")
    print(f"Request ID: {result.request_id}")
    print(f"Input tokens: {result.input_tokens}")
    print(f"Output tokens: {result.output_tokens}")
    print(f"Retry count: {result.retry_count}")
    print(f"Total cost: ${result.total_cost}")
    print(f"Response time: {result.response_time:.2f}s")
    
    if result.status == 'success':
        print(f"\nОтвет:")
        print(result.response.content)
    else:
        print(f"\nОшибка: {result.error_message}")


def example_gigachat_usage():
    """Пример использования с GigaChat"""
    print("\n" + "="*50)
    print("ПРИМЕР С GIGACHAT")
    print("="*50)
    
    # Создаем провайдер GigaChat
    credentials = "your-credentials-here"
    provider = GigaChatProvider(credentials=credentials)
    
    # Создаем пайплайн
    pipeline = LLMPipeline(provider)
    
    # Создаем запрос
    request = LLMRequest(
        request_id="example_2",
        system_prompt="Ты эксперт по программированию. Помогай с кодом.",
        user_prompt="Напиши простую функцию на Python для вычисления факториала.",
        context="Функция должна быть рекурсивной",
        is_json=False
    )
    
    # Обрабатываем запрос
    result = pipeline.process_request(request)
    
    # Выводим результат
    print(f"Статус: {result.status}")
    if result.status == 'success':
        print(f"\nОтвет:")
        print(result.response.content)
    else:
        print(f"\nОшибка: {result.error_message}")


def example_openrouter_usage():
    """Пример использования с OpenRouter"""
    print("\n" + "="*50)
    print("ПРИМЕР С OPENROUTER")
    print("="*50)
    
    # Создаем провайдер OpenRouter
    api_key = os.getenv("OPENROUTER_API_KEY", "your-api-key-here")
    provider = OpenRouterProvider(api_key=api_key, model="anthropic/claude-3-haiku")
    
    # Создаем пайплайн
    pipeline = LLMPipeline(provider)
    
    # Создаем запрос
    request = LLMRequest(
        request_id="openrouter_example",
        system_prompt="Ты полезный AI-ассистент. Отвечай кратко и по делу.",
        user_prompt="Объясни, что такое блокчейн в двух предложениях.",
        context="",
        additional_data={"language": "русский"},
        is_json=False
    )
    
    # Обрабатываем запрос
    result = pipeline.process_request(request)
    
    # Выводим результат
    print(f"Статус: {result.status}")
    print(f"Request ID: {result.request_id}")
    print(f"Input tokens: {result.input_tokens}")
    print(f"Output tokens: {result.output_tokens}")
    print(f"Retry count: {result.retry_count}")
    print(f"Total cost: ${result.total_cost}")
    print(f"Response time: {result.response_time:.2f}s")
    
    if result.status == 'success':
        print(f"\nОтвет:")
        print(result.response.content)
    else:
        print(f"\nОшибка: {result.error_message}")


def example_batch_processing():
    """Пример пакетной обработки"""
    print("\n" + "="*50)
    print("ПРИМЕР ПАКЕТНОЙ ОБРАБОТКИ")
    print("="*50)
    
    # Создаем провайдер (используем GigaChat для демонстрации)
    provider = GigaChatProvider(credentials="test")
    pipeline = LLMPipeline(provider)
    
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
    
    # Выводим результаты
    for result in results:
        print(f"\nЗапрос {result.request_id}:")
        print(f"  Статус: {result.status}")
        if result.status == 'success':
            print(f"  Ответ: {result.response.content[:100]}...")
        else:
            print(f"  Ошибка: {result.error_message}")
    
    # Выводим статистику
    stats = pipeline.get_statistics()
    if stats:
        print(f"\nСтатистика:")
        print(f"  Всего запросов: {stats['total_requests']}")
        print(f"  Успешных: {stats['successful_requests']}")
        print(f"  С ошибками: {stats['failed_requests']}")
        print(f"  Процент успеха: {stats['success_rate']:.1f}%")


def example_custom_prompt_template():
    """Пример использования кастомного шаблона промпта"""
    print("\n" + "="*50)
    print("ПРИМЕР С КАСТОМНЫМ ШАБЛОНОМ")
    print("="*50)
    
    # Создаем провайдер
    provider = GigaChatProvider(credentials="test")
    pipeline = LLMPipeline(provider)
    
    # Устанавливаем кастомный шаблон
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

Ответь на русском языке.
"""
    
    pipeline.set_prompt_template(custom_template)
    
    # Создаем запрос
    request = LLMRequest(
        request_id="custom_template",
        system_prompt="",  # Будет заменено в шаблоне
        user_prompt="Объясни принцип работы нейронных сетей",
        context="Для начинающих",
        additional_data={"ROLE": "эксперт по машинному обучению", "format": "простыми словами"},
        is_json=False
    )
    
    # Обрабатываем запрос
    result = pipeline.process_request(request)
    
    print(f"Статус: {result.status}")
    if result.status == 'success':
        print(f"\nОтвет:")
        print(result.response.content)
    else:
        print(f"\nОшибка: {result.error_message}")


def main():
    """Главная функция с примерами"""
    print("Примеры использования модуля LLM")
    print("="*50)
    
    try:
        # Пример с OpenAI (требует API ключ)
        # example_openai_usage()
        
        # Пример с GigaChat (заглушка)
        example_gigachat_usage()
        
        # Пример с OpenRouter (требует API ключ)
        # example_openrouter_usage()
        
        # Пример пакетной обработки
        example_batch_processing()
        
        # Пример с кастомным шаблоном
        example_custom_prompt_template()
        
    except Exception as e:
        logger.error(f"Ошибка в примерах: {e}")
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
