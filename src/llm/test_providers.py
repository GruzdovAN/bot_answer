#!/usr/bin/env python3
"""
Тесты для провайдеров LLM
"""

import unittest
from unittest.mock import Mock, patch
from .providers import OpenAIProvider, GigaChatProvider, DeepSeekProvider, OpenRouterProvider


class TestProviders(unittest.TestCase):
    """Тесты для провайдеров"""
    
    def test_openai_provider_initialization(self):
        """Тест инициализации OpenAI провайдера"""
        provider = OpenAIProvider(api_key="test-key", model="gpt-4o-mini")
        self.assertEqual(provider.api_key, "test-key")
        self.assertEqual(provider.model, "gpt-4o-mini")
        self.assertEqual(provider.temperature, 0.7)
    
    def test_gigachat_provider_initialization(self):
        """Тест инициализации GigaChat провайдера"""
        provider = GigaChatProvider(credentials="test-credentials")
        self.assertEqual(provider.credentials, "test-credentials")
        self.assertEqual(provider.model, "GigaChat")
        self.assertEqual(provider.temperature, 0.7)
    
    def test_deepseek_provider_initialization(self):
        """Тест инициализации DeepSeek провайдера"""
        provider = DeepSeekProvider(api_key="test-key", model="deepseek-chat")
        self.assertEqual(provider.api_key, "test-key")
        self.assertEqual(provider.model, "deepseek-chat")
        self.assertEqual(provider.temperature, 0.7)
    
    def test_openrouter_provider_initialization(self):
        """Тест инициализации OpenRouter провайдера"""
        provider = OpenRouterProvider(api_key="test-key", model="anthropic/claude-3-haiku")
        self.assertEqual(provider.api_key, "test-key")
        self.assertEqual(provider.model, "anthropic/claude-3-haiku")
        self.assertEqual(provider.temperature, 0.7)
    
    def test_gigachat_get_response(self):
        """Тест получения ответа от GigaChat"""
        provider = GigaChatProvider(credentials="test-credentials")
        
        messages = [
            {"role": "user", "content": "Тестовое сообщение"}
        ]
        
        response, tokens = provider.get_response(messages, is_json=False)
        
        self.assertIsNotNone(response)
        self.assertIsInstance(tokens, int)
        self.assertGreater(tokens, 0)
        self.assertIn("Тестовый ответ", response.content)


if __name__ == '__main__':
    unittest.main()
