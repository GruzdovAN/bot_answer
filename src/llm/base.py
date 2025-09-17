"""
Базовые классы для работы с LLM
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class NoSerializeNoneModel(BaseModel):
    """Базовый класс без сериализации `None` значений"""

    def model_dump(self, **kwargs):
        kwargs.setdefault("exclude_none", True)
        kwargs.setdefault("by_alias", True)
        return super().model_dump(**kwargs)

    def model_dump_json(self, **kwargs) -> str:
        return json.dumps(
            self.model_dump(**kwargs), ensure_ascii=False, **kwargs)


class LLMResponse(NoSerializeNoneModel):
    """Структура ответа LLM"""
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PromptParameters:
    """Параметры для формирования промпта"""
    system_prompt: str = ""
    user_prompt: str = ""
    context: str = ""
    additional_data: Optional[Dict[str, Any]] = None


class LLMProvider:
    """Базовый класс для LLM провайдеров"""
    
    def __init__(self, api_key: str, model: str, temperature: float = 0.7):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
    
    def get_response(self, messages: List[Dict[str, str]], is_json: bool = False) -> Tuple[LLMResponse, int]:
        """
        Получить ответ от LLM
        
        Args:
            messages: Список сообщений для LLM
            is_json: Ожидать ли JSON ответ
            
        Returns:
            Tuple[LLMResponse, int]: Ответ LLM и количество выходных токенов
        """
        raise NotImplementedError
    
    def validate_response(self, response: str, is_json: bool = False) -> LLMResponse:
        """
        Валидировать и преобразовать ответ LLM
        
        Args:
            response: Сырой ответ от LLM
            is_json: Ожидать ли JSON ответ
            
        Returns:
            LLMResponse: Валидированный ответ
        """
        if is_json:
            try:
                response_dict = json.loads(response)
                return LLMResponse(content=response_dict.get('content', response), metadata=response_dict)
            except json.JSONDecodeError as e:
                raise ValueError(f"LLM вернул некорректный JSON: {e}. Ответ: {response[:500]}...")
        else:
            return LLMResponse(content=response)
