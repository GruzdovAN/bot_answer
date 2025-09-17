"""
Универсальный строитель промптов для LLM
"""

import re
import logging
from typing import Dict, List, Optional, Any
from .base import PromptParameters

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Универсальный строитель промптов"""
    
    def __init__(self, template: Optional[str] = None):
        """
        Инициализация строителя промптов
        
        Args:
            template: Базовый шаблон промпта. Если не указан, используется стандартный
        """
        self.template = template or self._get_default_template()
    
    def _get_default_template(self) -> str:
        """Получить стандартный шаблон промпта"""
        return """{{SYSTEM_PROMPT}}

{{#if CONTEXT}}
## Контекст
{{CONTEXT}}
{{/if}}

{{#if ADDITIONAL_DATA}}
## Дополнительная информация
{{ADDITIONAL_DATA}}
{{/if}}

{{USER_PROMPT}}"""
    
    def build_prompt(self, parameters: PromptParameters) -> str:
        """
        Формирует полный промпт на основе параметров
        
        Args:
            parameters: Параметры для формирования промпта
            
        Returns:
            str: Сформированный промпт
        """
        prompt = self.template
        
        # Заменяем основные плейсхолдеры
        replacements = {
            "{{SYSTEM_PROMPT}}": parameters.system_prompt,
            "{{USER_PROMPT}}": parameters.user_prompt,
            "{{CONTEXT}}": parameters.context,
        }
        
        # Добавляем дополнительные данные
        if parameters.additional_data:
            additional_text = self._format_additional_data(parameters.additional_data)
            replacements["{{ADDITIONAL_DATA}}"] = additional_text
        else:
            replacements["{{ADDITIONAL_DATA}}"] = ""
        
        # Выполняем замены
        for placeholder, value in replacements.items():
            prompt = prompt.replace(placeholder, str(value))
        
        # Обрабатываем условные конструкции
        prompt = self._process_conditional_blocks(prompt, parameters)
        
        return prompt
    
    def _format_additional_data(self, data: Dict[str, Any]) -> str:
        """
        Форматирует дополнительные данные в текстовый вид
        
        Args:
            data: Словарь с дополнительными данными
            
        Returns:
            str: Отформатированные данные
        """
        if not data:
            return ""
        
        formatted_parts = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                formatted_parts.append(f"{key}: {self._format_complex_value(value)}")
            else:
                formatted_parts.append(f"{key}: {value}")
        
        return "\n".join(formatted_parts)
    
    def _format_complex_value(self, value: Any) -> str:
        """
        Форматирует сложные значения (словари, списки)
        
        Args:
            value: Значение для форматирования
            
        Returns:
            str: Отформатированное значение
        """
        if isinstance(value, dict):
            return "\n".join([f"  {k}: {v}" for k, v in value.items()])
        elif isinstance(value, list):
            return "\n".join([f"  - {item}" for item in value])
        else:
            return str(value)
    
    def _process_conditional_blocks(self, prompt: str, parameters: PromptParameters) -> str:
        """
        Обрабатывает условные блоки {{#if PLACEHOLDER}}...{{/if}}
        
        Args:
            prompt: Промпт с условными блоками
            parameters: Параметры для проверки условий
            
        Returns:
            str: Промпт с обработанными условными блоками
        """
        # Паттерн для условных блоков
        pattern = r'\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}'
        
        def replace_conditional(match):
            placeholder = match.group(1)
            content = match.group(2)
            
            # Проверяем, есть ли значение для плейсхолдера
            if hasattr(parameters, placeholder.lower()):
                value = getattr(parameters, placeholder.lower())
                if value and str(value).strip():
                    return content
            elif parameters.additional_data and placeholder.lower() in parameters.additional_data:
                value = parameters.additional_data[placeholder.lower()]
                if value and str(value).strip():
                    return content
            return ""
        
        return re.sub(pattern, replace_conditional, prompt, flags=re.DOTALL)
    
    def build_messages(self, parameters: PromptParameters) -> List[Dict[str, str]]:
        """
        Формирует список сообщений для LLM
        
        Args:
            parameters: Параметры для формирования сообщений
            
        Returns:
            List[Dict[str, str]]: Список сообщений
        """
        messages = []
        
        # Добавляем системное сообщение если есть
        if parameters.system_prompt:
            messages.append({
                "role": "system",
                "content": parameters.system_prompt
            })
        
        # Формируем пользовательское сообщение
        user_content = parameters.user_prompt
        
        # Добавляем контекст если есть
        if parameters.context:
            user_content = f"{parameters.context}\n\n{user_content}"
        
        # Добавляем дополнительные данные если есть
        if parameters.additional_data:
            additional_text = self._format_additional_data(parameters.additional_data)
            user_content = f"{additional_text}\n\n{user_content}"
        
        messages.append({
            "role": "user",
            "content": user_content
        })
        
        return messages
    
    def set_template(self, template: str):
        """
        Установить новый шаблон промпта
        
        Args:
            template: Новый шаблон
        """
        self.template = template
    
    def get_template(self) -> str:
        """
        Получить текущий шаблон промпта
        
        Returns:
            str: Текущий шаблон
        """
        return self.template
