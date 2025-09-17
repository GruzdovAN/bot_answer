"""
Модуль для работы с LLM (Large Language Models)

Этот модуль предоставляет универсальный интерфейс для работы с различными
LLM провайдерами без привязки к конкретной предметной области.
"""

from .base import LLMProvider, LLMResponse, PromptParameters
from .providers import OpenAIProvider, GigaChatProvider, DeepSeekProvider, OpenRouterProvider
from .prompt_builder import PromptBuilder
from .pipeline import LLMPipeline, LLMRequest, LLMResult
from .utils import TokenCounter, CostCalculator, RetryManager, StatisticsCollector

__all__ = [
    'LLMProvider',
    'LLMResponse', 
    'PromptParameters',
    'OpenAIProvider',
    'GigaChatProvider',
    'DeepSeekProvider',
    'OpenRouterProvider',
    'PromptBuilder',
    'LLMPipeline',
    'LLMRequest',
    'LLMResult',
    'TokenCounter',
    'CostCalculator',
    'RetryManager',
    'StatisticsCollector'
]
