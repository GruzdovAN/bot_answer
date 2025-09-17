"""
Утилиты для работы с LLM
"""

import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class TokenCounter:
    """Счетчик токенов (упрощенная версия)"""
    
    @staticmethod
    def count_tokens(text: str) -> int:
        """
        Подсчет токенов (приблизительный)
        
        Args:
            text: Текст для подсчета токенов
            
        Returns:
            int: Приблизительное количество токенов
        """
        if not text:
            return 0
        
        # Упрощенный подсчет: примерно 4 символа = 1 токен
        # В реальном проекте здесь можно использовать tiktoken или другие библиотеки
        return len(text) // 4
    
    @staticmethod
    def count_tokens_in_messages(messages: list) -> int:
        """
        Подсчет токенов в списке сообщений
        
        Args:
            messages: Список сообщений для LLM
            
        Returns:
            int: Общее количество токенов
        """
        total_tokens = 0
        for message in messages:
            if isinstance(message, dict) and 'content' in message:
                total_tokens += TokenCounter.count_tokens(message['content'])
            elif isinstance(message, str):
                total_tokens += TokenCounter.count_tokens(message)
        return total_tokens


@dataclass
class CostCalculator:
    """Калькулятор стоимости запросов к LLM"""
    
    # Примерные цены для разных моделей (USD за 1K токенов)
    PRICING = {
        'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006},
        'gpt-4o': {'input': 0.005, 'output': 0.015},
        'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
        'deepseek-chat': {'input': 0.00014, 'output': 0.00028},
        'claude-3-haiku-20240307': {'input': 0.00025, 'output': 0.00125},
        'claude-3-sonnet-20240229': {'input': 0.003, 'output': 0.015},
    }
    
    @classmethod
    def calculate_cost(cls, model: str, input_tokens: int, output_tokens: int) -> float:
        """
        Вычисляет стоимость запроса
        
        Args:
            model: Название модели
            input_tokens: Количество входных токенов
            output_tokens: Количество выходных токенов
            
        Returns:
            float: Стоимость в USD
        """
        if model not in cls.PRICING:
            logger.warning(f"Цены для модели {model} не найдены, используется приблизительная оценка")
            # Используем средние цены как fallback
            input_cost_per_1k = 0.001
            output_cost_per_1k = 0.003
        else:
            pricing = cls.PRICING[model]
            input_cost_per_1k = pricing['input']
            output_cost_per_1k = pricing['output']
        
        input_cost = (input_tokens / 1000) * input_cost_per_1k
        output_cost = (output_tokens / 1000) * output_cost_per_1k
        
        return round(input_cost + output_cost, 6)


class RetryManager:
    """Менеджер повторных попыток"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        """
        Инициализация менеджера повторных попыток
        
        Args:
            max_retries: Максимальное количество попыток
            base_delay: Базовая задержка в секундах
            max_delay: Максимальная задержка в секундах
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def get_delay(self, attempt: int) -> float:
        """
        Вычисляет задержку для попытки
        
        Args:
            attempt: Номер попытки (начиная с 1)
            
        Returns:
            float: Задержка в секундах
        """
        # Экспоненциальная задержка с jitter
        delay = min(self.base_delay * (2 ** (attempt - 1)), self.max_delay)
        # Добавляем случайный jitter (±25%)
        import random
        jitter = delay * 0.25 * (2 * random.random() - 1)
        return max(0, delay + jitter)
    
    def should_retry(self, attempt: int, exception: Exception) -> bool:
        """
        Определяет, стоит ли повторить попытку
        
        Args:
            attempt: Номер попытки
            exception: Исключение, которое произошло
            
        Returns:
            bool: True если стоит повторить
        """
        if attempt >= self.max_retries:
            return False
        
        # Список исключений, при которых стоит повторить попытку
        retryable_exceptions = (
            ConnectionError,
            TimeoutError,
            # Добавьте другие типы исключений по необходимости
        )
        
        return isinstance(exception, retryable_exceptions)


class StatisticsCollector:
    """Сборщик статистики использования LLM"""
    
    def __init__(self):
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'total_cost': 0.0,
            'requests_by_provider': {},
            'requests_by_model': {},
            'average_response_time': 0.0,
            'response_times': []
        }
    
    def record_request(self, provider: str, model: str, success: bool, 
                      input_tokens: int = 0, output_tokens: int = 0, 
                      cost: float = 0.0, response_time: float = 0.0):
        """
        Записывает статистику запроса
        
        Args:
            provider: Название провайдера
            model: Название модели
            success: Успешность запроса
            input_tokens: Количество входных токенов
            output_tokens: Количество выходных токенов
            cost: Стоимость запроса
            response_time: Время ответа в секундах
        """
        self.stats['total_requests'] += 1
        
        if success:
            self.stats['successful_requests'] += 1
        else:
            self.stats['failed_requests'] += 1
        
        self.stats['total_input_tokens'] += input_tokens
        self.stats['total_output_tokens'] += output_tokens
        self.stats['total_cost'] += cost
        
        # Статистика по провайдерам
        if provider not in self.stats['requests_by_provider']:
            self.stats['requests_by_provider'][provider] = 0
        self.stats['requests_by_provider'][provider] += 1
        
        # Статистика по моделям
        if model not in self.stats['requests_by_model']:
            self.stats['requests_by_model'][model] = 0
        self.stats['requests_by_model'][model] += 1
        
        # Время ответа
        self.stats['response_times'].append(response_time)
        if len(self.stats['response_times']) > 100:  # Ограничиваем размер списка
            self.stats['response_times'] = self.stats['response_times'][-100:]
        
        self.stats['average_response_time'] = sum(self.stats['response_times']) / len(self.stats['response_times'])
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику
        
        Returns:
            Dict[str, Any]: Словарь со статистикой
        """
        stats = self.stats.copy()
        
        # Добавляем вычисляемые метрики
        total = stats['total_requests']
        if total > 0:
            stats['success_rate'] = (stats['successful_requests'] / total) * 100
            stats['average_input_tokens'] = stats['total_input_tokens'] / total
            stats['average_output_tokens'] = stats['total_output_tokens'] / total
            stats['average_cost_per_request'] = stats['total_cost'] / total
        else:
            stats['success_rate'] = 0
            stats['average_input_tokens'] = 0
            stats['average_output_tokens'] = 0
            stats['average_cost_per_request'] = 0
        
        return stats
    
    def reset_statistics(self):
        """Сбросить статистику"""
        self.__init__()
