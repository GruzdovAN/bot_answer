#!/usr/bin/env python3
"""
Базовые тесты для модуля LLM
"""

import unittest
from unittest.mock import Mock, patch
from .base import LLMResponse, PromptParameters
from .providers import GigaChatProvider
from .pipeline import LLMPipeline, LLMRequest
from .utils import TokenCounter, CostCalculator


class TestLLMResponse(unittest.TestCase):
    """Тесты для LLMResponse"""
    
    def test_basic_response(self):
        """Тест базового ответа"""
        response = LLMResponse(content="Тестовый ответ")
        self.assertEqual(response.content, "Тестовый ответ")
        self.assertIsNone(response.metadata)
    
    def test_response_with_metadata(self):
        """Тест ответа с метаданными"""
        metadata = {"provider": "test", "model": "test-model"}
        response = LLMResponse(content="Тестовый ответ", metadata=metadata)
        self.assertEqual(response.content, "Тестовый ответ")
        self.assertEqual(response.metadata, metadata)


class TestPromptParameters(unittest.TestCase):
    """Тесты для PromptParameters"""
    
    def test_basic_parameters(self):
        """Тест базовых параметров"""
        params = PromptParameters(
            system_prompt="Системный промпт",
            user_prompt="Пользовательский промпт"
        )
        self.assertEqual(params.system_prompt, "Системный промпт")
        self.assertEqual(params.user_prompt, "Пользовательский промпт")
        self.assertEqual(params.context, "")
        self.assertIsNone(params.additional_data)


class TestTokenCounter(unittest.TestCase):
    """Тесты для TokenCounter"""
    
    def test_count_tokens(self):
        """Тест подсчета токенов"""
        counter = TokenCounter()
        
        # Пустая строка
        self.assertEqual(counter.count_tokens(""), 0)
        
        # Обычная строка
        tokens = counter.count_tokens("Привет, мир!")
        self.assertGreater(tokens, 0)
        
        # Длинная строка
        long_text = "Это очень длинный текст " * 100
        tokens_long = counter.count_tokens(long_text)
        self.assertGreater(tokens_long, tokens)
    
    def test_count_tokens_in_messages(self):
        """Тест подсчета токенов в сообщениях"""
        counter = TokenCounter()
        
        messages = [
            {"role": "system", "content": "Системное сообщение"},
            {"role": "user", "content": "Пользовательское сообщение"}
        ]
        
        tokens = counter.count_tokens_in_messages(messages)
        self.assertGreater(tokens, 0)


class TestCostCalculator(unittest.TestCase):
    """Тесты для CostCalculator"""
    
    def test_calculate_cost(self):
        """Тест расчета стоимости"""
        calculator = CostCalculator()
        
        # Тест с известной моделью
        cost = calculator.calculate_cost("gpt-4o-mini", 100, 50)
        self.assertGreater(cost, 0)
        
        # Тест с неизвестной моделью
        cost_unknown = calculator.calculate_cost("unknown-model", 100, 50)
        self.assertGreater(cost_unknown, 0)
    
    def test_zero_tokens(self):
        """Тест с нулевыми токенами"""
        calculator = CostCalculator()
        cost = calculator.calculate_cost("gpt-4o-mini", 0, 0)
        self.assertEqual(cost, 0)


class TestGigaChatProvider(unittest.TestCase):
    """Тесты для GigaChatProvider"""
    
    def test_initialization(self):
        """Тест инициализации провайдера"""
        provider = GigaChatProvider(credentials="test-credentials")
        self.assertEqual(provider.credentials, "test-credentials")
        self.assertEqual(provider.model, "GigaChat")
        self.assertEqual(provider.temperature, 0.7)
    
    def test_get_response(self):
        """Тест получения ответа"""
        provider = GigaChatProvider(credentials="test-credentials")
        
        messages = [
            {"role": "user", "content": "Тестовое сообщение"}
        ]
        
        response, tokens = provider.get_response(messages, is_json=False)
        
        self.assertIsInstance(response, LLMResponse)
        self.assertIsInstance(tokens, int)
        self.assertGreater(tokens, 0)


class TestLLMPipeline(unittest.TestCase):
    """Тесты для LLMPipeline"""
    
    def setUp(self):
        """Настройка для тестов"""
        self.provider = GigaChatProvider(credentials="test-credentials")
        self.pipeline = LLMPipeline(self.provider)
    
    def test_initialization(self):
        """Тест инициализации пайплайна"""
        self.assertEqual(self.pipeline.provider, self.provider)
        self.assertIsNotNone(self.pipeline.prompt_builder)
        self.assertIsNotNone(self.pipeline.token_counter)
        self.assertIsNotNone(self.pipeline.statistics)
    
    def test_process_request(self):
        """Тест обработки запроса"""
        request = LLMRequest(
            request_id="test_1",
            system_prompt="Ты тестовый ассистент.",
            user_prompt="Привет!",
            is_json=False
        )
        
        result = self.pipeline.process_request(request)
        
        self.assertEqual(result.request_id, "test_1")
        self.assertEqual(result.status, "success")
        self.assertIsNotNone(result.response)
        self.assertGreater(result.input_tokens, 0)
        self.assertGreater(result.output_tokens, 0)
        self.assertGreaterEqual(result.total_cost, 0)
    
    def test_get_statistics(self):
        """Тест получения статистики"""
        stats = self.pipeline.get_statistics()
        self.assertIsNotNone(stats)
        self.assertIn('total_requests', stats)
        self.assertIn('successful_requests', stats)
        self.assertIn('failed_requests', stats)
    
    def test_set_retry_config(self):
        """Тест настройки ретраев"""
        self.pipeline.set_retry_config(max_retries=5, base_delay=2.0)
        self.assertEqual(self.pipeline.retry_manager.max_retries, 5)
        self.assertEqual(self.pipeline.retry_manager.base_delay, 2.0)


if __name__ == '__main__':
    unittest.main()
