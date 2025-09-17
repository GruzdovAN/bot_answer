"""
Основной класс пайплайна для работы с LLM
"""

import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from .base import LLMProvider, LLMResponse, PromptParameters
from .prompt_builder import PromptBuilder
from .utils import TokenCounter, CostCalculator, RetryManager, StatisticsCollector

logger = logging.getLogger(__name__)


@dataclass
class LLMRequest:
    """Структура запроса к LLM"""
    request_id: str
    system_prompt: str
    user_prompt: str
    context: str = ""
    additional_data: Optional[Dict[str, Any]] = None
    is_json: bool = False
    max_retries: int = 3


@dataclass
class LLMResult:
    """Результат выполнения запроса к LLM"""
    request_id: str
    response: Optional[LLMResponse]
    input_tokens: int
    output_tokens: int
    total_cost: float
    retry_count: int
    response_time: float
    status: str  # 'success' или 'error'
    error_message: Optional[str] = None
    timestamp: float = 0.0


class LLMPipeline:
    """Основной класс пайплайна LLM"""
    
    def __init__(self, provider: LLMProvider, enable_statistics: bool = True):
        """
        Инициализация пайплайна
        
        Args:
            provider: Провайдер LLM
            enable_statistics: Включить сбор статистики
        """
        self.provider = provider
        self.prompt_builder = PromptBuilder()
        self.token_counter = TokenCounter()
        self.cost_calculator = CostCalculator()
        self.retry_manager = RetryManager()
        self.statistics = StatisticsCollector() if enable_statistics else None
        
        logger.info(f"LLM Pipeline инициализирован с провайдером: {provider.__class__.__name__}")
    
    def process_request(self, request: LLMRequest) -> LLMResult:
        """
        Обработать запрос к LLM
        
        Args:
            request: Запрос к LLM
            
        Returns:
            LLMResult: Результат обработки
        """
        start_time = time.time()
        logger.info(f"Обработка запроса {request.request_id}")
        
        # Формируем параметры промпта
        parameters = PromptParameters(
            system_prompt=request.system_prompt,
            user_prompt=request.user_prompt,
            context=request.context,
            additional_data=request.additional_data
        )
        
        # Формируем сообщения для LLM
        messages = self.prompt_builder.build_messages(parameters)
        
        # Подсчитываем токены
        input_tokens = self.token_counter.count_tokens_in_messages(messages)
        
        try:
            # Получаем ответ от LLM с ретраями
            response, output_tokens, retry_count = self._get_response_with_retry(
                messages, request.is_json, request.max_retries
            )
            
            # Вычисляем стоимость
            total_cost = self.cost_calculator.calculate_cost(
                self.provider.model, input_tokens, output_tokens
            )
            
            response_time = time.time() - start_time
            
            # Создаем результат
            result = LLMResult(
                request_id=request.request_id,
                response=response,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_cost=total_cost,
                retry_count=retry_count,
                response_time=response_time,
                status='success',
                timestamp=time.time()
            )
            
            # Записываем статистику
            if self.statistics:
                self.statistics.record_request(
                    provider=self.provider.__class__.__name__,
                    model=self.provider.model,
                    success=True,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost=total_cost,
                    response_time=response_time
                )
            
            logger.info(f"Запрос {request.request_id} обработан успешно за {response_time:.2f}с")
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            error_message = str(e)
            
            logger.error(f"Ошибка обработки запроса {request.request_id}: {error_message}")
            
            # Создаем результат с ошибкой
            result = LLMResult(
                request_id=request.request_id,
                response=None,
                input_tokens=input_tokens,
                output_tokens=0,
                total_cost=0.0,
                retry_count=0,
                response_time=response_time,
                status='error',
                error_message=error_message,
                timestamp=time.time()
            )
            
            # Записываем статистику ошибки
            if self.statistics:
                self.statistics.record_request(
                    provider=self.provider.__class__.__name__,
                    model=self.provider.model,
                    success=False,
                    input_tokens=input_tokens,
                    output_tokens=0,
                    cost=0.0,
                    response_time=response_time
                )
            
            return result
    
    def _get_response_with_retry(
        self, 
        messages: List[Dict[str, str]], 
        is_json: bool = False,
        max_retries: int = 3
    ) -> Tuple[LLMResponse, int, int]:
        """
        Получить ответ от LLM с повторными попытками
        
        Args:
            messages: Сообщения для LLM
            is_json: Ожидать ли JSON ответ
            max_retries: Максимальное количество попыток
            
        Returns:
            Tuple[LLMResponse, int, int]: Ответ, количество токенов, количество попыток
        """
        last_exception = None
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Попытка {attempt}/{max_retries} запроса к LLM")
                response, output_tokens = self.provider.get_response(messages, is_json)
                logger.info(f"LLM ответ получен успешно. Output tokens: {output_tokens}, попыток: {attempt}")
                return response, output_tokens, attempt
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Попытка {attempt} неудачна: {e}")
                
                # Проверяем, стоит ли повторить попытку
                if not self.retry_manager.should_retry(attempt, e):
                    logger.error(f"Повторные попытки не рекомендуются для данного типа ошибки")
                    break
                
                # Ждем перед следующей попыткой
                if attempt < max_retries:
                    delay = self.retry_manager.get_delay(attempt)
                    logger.info(f"Ожидание {delay:.2f} сек перед следующей попыткой")
                    time.sleep(delay)
        
        # Все попытки исчерпаны
        logger.error(f"Все {max_retries} попыток исчерпаны")
        raise last_exception
    
    def process_batch(self, requests: List[LLMRequest]) -> List[LLMResult]:
        """
        Обработать пакет запросов
        
        Args:
            requests: Список запросов
            
        Returns:
            List[LLMResult]: Список результатов
        """
        logger.info(f"Обработка пакета из {len(requests)} запросов")
        results = []
        
        for request in requests:
            result = self.process_request(request)
            results.append(result)
        
        logger.info(f"Пакет обработан. Успешно: {sum(1 for r in results if r.status == 'success')}")
        return results
    
    def get_statistics(self) -> Optional[Dict[str, Any]]:
        """
        Получить статистику использования
        
        Returns:
            Optional[Dict[str, Any]]: Статистика или None если отключена
        """
        if self.statistics:
            return self.statistics.get_statistics()
        return None
    
    def reset_statistics(self):
        """Сбросить статистику"""
        if self.statistics:
            self.statistics.reset_statistics()
    
    def set_retry_config(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        """
        Настроить параметры повторных попыток
        
        Args:
            max_retries: Максимальное количество попыток
            base_delay: Базовая задержка в секундах
            max_delay: Максимальная задержка в секундах
        """
        self.retry_manager = RetryManager(max_retries, base_delay, max_delay)
        logger.info(f"Настройки повторных попыток обновлены: max_retries={max_retries}, base_delay={base_delay}")
    
    def set_prompt_template(self, template: str):
        """
        Установить новый шаблон промпта
        
        Args:
            template: Новый шаблон
        """
        self.prompt_builder.set_template(template)
        logger.info("Шаблон промпта обновлен")
    
    def get_provider_info(self) -> Dict[str, str]:
        """
        Получить информацию о провайдере
        
        Returns:
            Dict[str, str]: Информация о провайдере
        """
        return {
            'provider': self.provider.__class__.__name__,
            'model': self.provider.model,
            'temperature': str(self.provider.temperature)
        }
