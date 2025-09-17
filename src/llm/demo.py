#!/usr/bin/env python3
"""
Демонстрация возможностей модуля LLM

Этот файл показывает основные возможности модуля для работы с LLM
в различных сценариях использования.
"""

import os
import logging
from typing import Dict, Any

from .pipeline import LLMPipeline, LLMRequest
from .providers import GigaChatProvider, OpenRouterProvider

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def demo_basic_usage():
    """Демонстрация базового использования"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ: Базовое использование")
    print("="*60)
    
    # Создаем провайдер (используем GigaChat для демонстрации)
    provider = GigaChatProvider(credentials="demo-credentials")
    
    # Создаем пайплайн
    pipeline = LLMPipeline(provider)
    
    # Создаем простой запрос
    request = LLMRequest(
        request_id="demo_basic",
        system_prompt="Ты полезный AI-ассистент. Отвечай кратко и по делу.",
        user_prompt="Объясни, что такое искусственный интеллект в двух предложениях.",
        is_json=False
    )
    
    print(f"Отправляем запрос: {request.user_prompt}")
    
    # Обрабатываем запрос
    result = pipeline.process_request(request)
    
    # Выводим результат
    print(f"\nРезультат:")
    print(f"  Статус: {result.status}")
    print(f"  Время ответа: {result.response_time:.2f}с")
    print(f"  Входные токены: {result.input_tokens}")
    print(f"  Выходные токены: {result.output_tokens}")
    print(f"  Стоимость: ${result.total_cost:.4f}")
    
    if result.status == 'success':
        print(f"\nОтвет LLM:")
        print(f"  {result.response.content}")
    else:
        print(f"\nОшибка: {result.error_message}")


def demo_context_usage():
    """Демонстрация использования контекста"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ: Использование контекста")
    print("="*60)
    
    provider = GigaChatProvider(credentials="demo-credentials")
    pipeline = LLMPipeline(provider)
    
    # Запрос с контекстом
    request = LLMRequest(
        request_id="demo_context",
        system_prompt="Ты эксперт по программированию на Python.",
        user_prompt="Напиши функцию для вычисления среднего значения списка чисел.",
        context="Функция должна быть эффективной и обрабатывать пустые списки.",
        additional_data={
            "style": "функциональный",
            "include_docstring": True,
            "add_examples": True
        },
        is_json=False
    )
    
    print(f"Запрос с контекстом:")
    print(f"  Основной запрос: {request.user_prompt}")
    print(f"  Контекст: {request.context}")
    print(f"  Дополнительные данные: {request.additional_data}")
    
    result = pipeline.process_request(request)
    
    print(f"\nРезультат:")
    print(f"  Статус: {result.status}")
    
    if result.status == 'success':
        print(f"\nОтвет LLM:")
        print(result.response.content)
    else:
        print(f"\nОшибка: {result.error_message}")


def demo_batch_processing():
    """Демонстрация пакетной обработки"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ: Пакетная обработка")
    print("="*60)
    
    provider = GigaChatProvider(credentials="demo-credentials")
    pipeline = LLMPipeline(provider)
    
    # Создаем несколько запросов
    requests = [
        LLMRequest(
            request_id=f"batch_math_{i}",
            system_prompt="Ты помощник по математике.",
            user_prompt=f"Реши уравнение: {i}x + {i+1} = {i*2 + 1}",
            is_json=False
        )
        for i in range(1, 4)
    ]
    
    print(f"Обрабатываем пакет из {len(requests)} запросов...")
    
    # Обрабатываем пакет
    results = pipeline.process_batch(requests)
    
    # Выводим результаты
    print(f"\nРезультаты пакетной обработки:")
    for result in results:
        print(f"\n  Запрос {result.request_id}:")
        print(f"    Статус: {result.status}")
        print(f"    Время: {result.response_time:.2f}с")
        print(f"    Токены: {result.input_tokens} → {result.output_tokens}")
        
        if result.status == 'success':
            print(f"    Ответ: {result.response.content[:100]}...")
        else:
            print(f"    Ошибка: {result.error_message}")
    
    # Выводим общую статистику
    stats = pipeline.get_statistics()
    print(f"\nОбщая статистика:")
    print(f"  Всего запросов: {stats['total_requests']}")
    print(f"  Успешных: {stats['successful_requests']}")
    print(f"  С ошибками: {stats['failed_requests']}")
    print(f"  Процент успеха: {stats['success_rate']:.1f}%")
    print(f"  Общая стоимость: ${stats['total_cost']:.4f}")


def demo_custom_template():
    """Демонстрация кастомного шаблона промпта"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ: Кастомный шаблон промпта")
    print("="*60)
    
    provider = GigaChatProvider(credentials="demo-credentials")
    pipeline = LLMPipeline(provider)
    
    # Устанавливаем кастомный шаблон
    custom_template = """
Ты {{ROLE}} с опытом {{EXPERIENCE}} лет.

{{#if CONTEXT}}
Контекст задачи: {{CONTEXT}}
{{/if}}

Задача: {{USER_PROMPT}}

{{#if ADDITIONAL_DATA}}
Дополнительные требования:
{{ADDITIONAL_DATA}}
{{/if}}

Отвечай на русском языке, используя {{STYLE}} стиль.
"""
    
    pipeline.set_prompt_template(custom_template)
    
    # Создаем запрос с данными для шаблона
    request = LLMRequest(
        request_id="demo_custom_template",
        system_prompt="",  # Будет заменено в шаблоне
        user_prompt="Объясни принцип работы блокчейна",
        context="Для начинающих разработчиков",
        additional_data={
            "ROLE": "эксперт по криптографии",
            "EXPERIENCE": "10",
            "STYLE": "простой и понятный"
        },
        is_json=False
    )
    
    print(f"Используем кастомный шаблон с переменными:")
    print(f"  ROLE: {request.additional_data['ROLE']}")
    print(f"  EXPERIENCE: {request.additional_data['EXPERIENCE']}")
    print(f"  STYLE: {request.additional_data['STYLE']}")
    print(f"  Контекст: {request.context}")
    
    result = pipeline.process_request(request)
    
    print(f"\nРезультат:")
    print(f"  Статус: {result.status}")
    
    if result.status == 'success':
        print(f"\nОтвет LLM:")
        print(result.response.content)
    else:
        print(f"\nОшибка: {result.error_message}")


def demo_statistics():
    """Демонстрация работы со статистикой"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ: Статистика и мониторинг")
    print("="*60)
    
    provider = GigaChatProvider(credentials="demo-credentials")
    pipeline = LLMPipeline(provider)
    
    # Выполняем несколько запросов для накопления статистики
    test_requests = [
        LLMRequest(
            request_id=f"stats_test_{i}",
            system_prompt="Ты помощник.",
            user_prompt=f"Ответь на вопрос номер {i}",
            is_json=False
        )
        for i in range(1, 6)
    ]
    
    print("Выполняем тестовые запросы для накопления статистики...")
    
    for request in test_requests:
        result = pipeline.process_request(request)
        print(f"  Запрос {request.request_id}: {result.status}")
    
    # Получаем и выводим статистику
    stats = pipeline.get_statistics()
    
    print(f"\nДетальная статистика:")
    print(f"  Всего запросов: {stats['total_requests']}")
    print(f"  Успешных: {stats['successful_requests']}")
    print(f"  С ошибками: {stats['failed_requests']}")
    print(f"  Процент успеха: {stats['success_rate']:.1f}%")
    print(f"  Общие токены: {stats['total_input_tokens']} → {stats['total_output_tokens']}")
    print(f"  Средние токены: {stats['average_input_tokens']:.1f} → {stats['average_output_tokens']:.1f}")
    print(f"  Общая стоимость: ${stats['total_cost']:.4f}")
    print(f"  Средняя стоимость: ${stats['average_cost_per_request']:.4f}")
    print(f"  Среднее время ответа: {stats['average_response_time']:.2f}с")
    
    print(f"\nСтатистика по провайдерам:")
    for provider_name, count in stats['requests_by_provider'].items():
        print(f"  {provider_name}: {count} запросов")
    
    print(f"\nСтатистика по моделям:")
    for model_name, count in stats['requests_by_model'].items():
        print(f"  {model_name}: {count} запросов")


def main():
    """Главная функция демонстрации"""
    print("ДЕМОНСТРАЦИЯ МОДУЛЯ LLM")
    print("="*60)
    print("Этот модуль предоставляет универсальный интерфейс для работы с LLM")
    print("без привязки к конкретной предметной области.")
    
    try:
        # Запускаем демонстрации
        demo_basic_usage()
        demo_context_usage()
        demo_batch_processing()
        demo_custom_template()
        demo_statistics()
        
        print("\n" + "="*60)
        print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
        print("="*60)
        print("Модуль LLM готов к использованию в ваших проектах!")
        
    except Exception as e:
        logger.error(f"Ошибка в демонстрации: {e}")
        print(f"\nОшибка: {e}")
        print("Убедитесь, что все зависимости установлены корректно.")


if __name__ == "__main__":
    main()
