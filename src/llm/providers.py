"""
Провайдеры для различных LLM сервисов
"""

import json
import logging
from typing import Dict, List, Tuple
import httpx
from openai import OpenAI

from .base import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """Провайдер OpenAI"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", temperature: float = 0.7, proxy_url: str = None):
        super().__init__(api_key, model, temperature)
        self.proxy_url = proxy_url
        
        # Создаем клиент с proxy если указан
        http_client = httpx.Client(proxy=proxy_url) if proxy_url else None
        self.client = OpenAI(
            api_key=api_key,
            http_client=http_client
        )
    
    def get_response(self, messages: List[Dict[str, str]], is_json: bool = False) -> Tuple[LLMResponse, int]:
        """Получить ответ от OpenAI"""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"} if is_json else None,
                temperature=self.temperature
            )
            
            answer = completion.choices[0].message.content
            output_tokens = completion.usage.completion_tokens
            
            response = self.validate_response(answer, is_json)
            
            logger.info(f"OpenAI успешно ответил. Output tokens: {output_tokens}")
            return response, output_tokens
            
        except Exception as e:
            logger.error(f"Ошибка OpenAI: {e}")
            raise


class GigaChatProvider(LLMProvider):
    """Провайдер GigaChat"""
    
    def __init__(self, credentials: str, model: str = "GigaChat", temperature: float = 0.7):
        super().__init__(credentials, model, temperature)
        self.credentials = credentials
        # В реальном проекте здесь был бы импорт GigaChat
        logger.warning("GigaChat провайдер требует установки библиотеки GigaChat")
    
    def get_response(self, messages: List[Dict[str, str]], is_json: bool = False) -> Tuple[LLMResponse, int]:
        """Получить ответ от GigaChat"""
        try:
            # Это заглушка - в реальном проекте здесь был бы вызов GigaChat API
            logger.warning("GigaChat провайдер не реализован в этом примере")
            
            # Возвращаем тестовый ответ
            response = LLMResponse(
                content="Тестовый ответ от GigaChat. Функциональность требует настройки GigaChat API.",
                metadata={"provider": "GigaChat", "model": self.model}
            )
            return response, 150
            
        except Exception as e:
            logger.error(f"Ошибка GigaChat: {e}")
            raise


class DeepSeekProvider(LLMProvider):
    """Провайдер DeepSeek"""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat", temperature: float = 0.7):
        super().__init__(api_key, model, temperature)
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    
    def get_response(self, messages: List[Dict[str, str]], is_json: bool = True) -> Tuple[LLMResponse, int]:
        """Получить ответ от DeepSeek"""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                stream=False
            )
            
            answer = completion.choices[0].message.content
            output_tokens = completion.usage.completion_tokens
            
            if is_json:
                try:
                    answer_dict = json.loads(answer)
                    response = LLMResponse(content=answer_dict.get('content', answer), metadata=answer_dict)
                except json.JSONDecodeError as e:
                    raise ValueError(f"DeepSeek вернул некорректный JSON: {e}. Ответ: {answer[:500]}...")
            else:
                response = LLMResponse(content=answer)
            
            logger.info(f"DeepSeek успешно ответил. Output tokens: {output_tokens}")
            return response, output_tokens
            
        except Exception as e:
            logger.error(f"Ошибка DeepSeek: {e}")
            raise


class OpenRouterProvider(LLMProvider):
    """Провайдер OpenRouter"""
    
    def __init__(self, api_key: str, model: str = "anthropic/claude-3-haiku", temperature: float = 0.7):
        super().__init__(api_key, model, temperature)
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
    
    def get_response(self, messages: List[Dict[str, str]], is_json: bool = True) -> Tuple[LLMResponse, int]:
        """Получить ответ от OpenRouter"""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            
            answer = completion.choices[0].message.content
            output_tokens = completion.usage.completion_tokens
            
            if is_json:
                try:
                    answer_dict = json.loads(answer)
                    response = LLMResponse(content=answer_dict.get('content', answer), metadata=answer_dict)
                except json.JSONDecodeError as e:
                    raise ValueError(f"OpenRouter вернул некорректный JSON: {e}. Ответ: {answer[:500]}...")
            else:
                response = LLMResponse(content=answer)
            
            logger.info(f"OpenRouter успешно ответил. Output tokens: {output_tokens}")
            return response, output_tokens
            
        except Exception as e:
            logger.error(f"Ошибка OpenRouter: {e}")
            raise
