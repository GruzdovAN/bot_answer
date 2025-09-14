# Модули для различных типов ботов
from .base_bot import BaseBot
from .smart_responder import SmartResponder
from .simple_responder import SimpleResponder
from .group_responder import GroupResponder

__all__ = ['BaseBot', 'SmartResponder', 'SimpleResponder', 'GroupResponder']
