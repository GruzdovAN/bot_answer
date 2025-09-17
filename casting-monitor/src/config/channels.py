"""
Конфигурация каналов для мониторинга
"""

from typing import List, Dict, Union

def get_monitored_channels() -> List[Union[str, int]]:
    """Получение списка каналов для мониторинга"""
    try:
        # Импортируем из существующей конфигурации
        import sys
        sys.path.append('/app/config')
        from castings_channels import CASTINGS_CHANNELS
        
        channels = []
        for channel_id, channel in CASTINGS_CHANNELS.items():
            if channel.get('enabled', True):
                # Если есть username, используем его
                if channel.get('username'):
                    channels.append(channel['username'])
                # Если нет username, используем числовой ID
                else:
                    channels.append(int(channel_id))
        
        return channels
    except ImportError:
        # Fallback конфигурация
        return [
            '@casting_channel_1',
            '@casting_channel_2',
            '@casting_channel_3'
        ]

def get_channel_config(username: str) -> Dict:
    """Получение конфигурации канала"""
    try:
        import sys
        sys.path.append('/app/config')
        from castings_channels import CASTINGS_CHANNELS
        for channel in CASTINGS_CHANNELS.values():
            if channel['username'] == username:
                return channel
    except ImportError:
        pass
    
    # Fallback конфигурация
    return {
        'username': username,
        'title': username,
        'enabled': True,
        'priority': 1
    }
