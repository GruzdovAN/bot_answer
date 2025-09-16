from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ChannelConfig:
    username: str
    enabled: bool
    parser_type: str
    days_back: int
    batch_size: int

class ChannelManager:
    def __init__(self):
        from config.channels import CHANNELS
        self.channels = {}
        self.load_config()
    
    def load_config(self):
        """Загрузка конфигурации каналов"""
        from config.channels import CHANNELS
        for name, channel_config in CHANNELS.items():
            self.channels[name] = ChannelConfig(**channel_config)
    
    def get_enabled_channels(self) -> List[ChannelConfig]:
        """Получение активных каналов"""
        return [ch for ch in self.channels.values() if ch.enabled]
    
    def get_channel_config(self, channel_name: str) -> ChannelConfig:
        """Получение конфигурации канала"""
        return self.channels.get(channel_name)
