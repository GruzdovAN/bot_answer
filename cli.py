#!/usr/bin/env python3
"""
CLI для управления Telegram Bot проектом
"""

import asyncio
import os
import sys
import click
from dotenv import load_dotenv

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Загружаем переменные окружения
load_dotenv()

@click.group()
def root():
    """
    CLI для управления Telegram Bot проектом
    
    Доступные команды:
    - scraper: управление скрапером
    - bot: управление ботом  
    - system: системные команды
    """

@root.group()
def scraper():
    """Управление скрапером"""
    pass

@scraper.command()
def test():
    """Тестировать компоненты скрапера"""
    click.echo("🧪 Тестирование компонентов скрапера...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'tests/test_components.py'], 
                              capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        click.echo("✅ Тестирование завершено успешно!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Ошибка при тестировании: {e}")
        if e.stderr:
            click.echo(f"Ошибка: {e.stderr}")

@scraper.command()
def check():
    """Проверить доступность канала"""
    click.echo("🔍 Проверка доступности канала...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'tests/check_channel.py'], 
                              capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        click.echo("✅ Проверка завершена успешно!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Ошибка при проверке: {e}")
        if e.stderr:
            click.echo(f"Ошибка: {e.stderr}")

@scraper.command()
def sessions():
    """Проверить доступность Telegram сессий"""
    click.echo("🔍 Проверка доступности Telegram сессий...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'scripts/check_sessions.py'], 
                              capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        click.echo("✅ Проверка сессий завершена успешно!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Ошибка при проверке сессий: {e}")
        if e.stderr:
            click.echo(f"Ошибка: {e.stderr}")

@scraper.command()
def simple():
    """Простой сбор данных"""
    click.echo("📥 Простой сбор данных...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'tests/simple_scraper.py'], 
                              capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        click.echo("✅ Сбор данных завершен успешно!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Ошибка при сборе данных: {e}")
        if e.stderr:
            click.echo(f"Ошибка: {e.stderr}")

@scraper.command()
@click.option('--session', is_flag=True, help='Использовать существующую сессию')
def run(session):
    """Запустить скрапер"""
    if session:
        click.echo("🚀 Запуск скрапера с существующей сессией...")
        script = 'scripts/run_scraper_with_session.py'
    else:
        click.echo("🚀 Запуск скрапера...")
        script = 'scripts/run_scraper.py'
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, script], 
                              capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        click.echo("✅ Скрапер завершен успешно!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Ошибка при запуске скрапера: {e}")
        if e.stderr:
            click.echo(f"Ошибка: {e.stderr}")

@scraper.command()
def analytics():
    """Показать аналитику"""
    click.echo("📊 Показ аналитики...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'tests/analytics.py'], 
                              capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        click.echo("✅ Аналитика показана успешно!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Ошибка при показе аналитики: {e}")
        if e.stderr:
            click.echo(f"Ошибка: {e.stderr}")

@scraper.command()
def test_castings():
    """Быстрый тест чтения каналов из папки @castings"""
    click.echo("🧪 Быстрый тест чтения каналов из папки @castings...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'quick_castings_test.py'], 
                              capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        click.echo("✅ Тест завершен успешно!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Ошибка при тестировании: {e}")
        if e.stderr:
            click.echo(f"Ошибка: {e.stderr}")

@scraper.command()
@click.option('--days', default=7, help='Количество дней назад для чтения сообщений')
@click.option('--limit', default=50, help='Лимит сообщений на канал')
def read_castings(days, limit):
    """Читать все каналы из папки @castings"""
    click.echo(f"📁 Чтение каналов из папки @castings...")
    click.echo(f"Период: {days} дней назад, лимит: {limit} сообщений на канал")
    try:
        import subprocess
        import os
        
        # Создаем временный скрипт с параметрами
        temp_script = f"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.read_castings_folder import CastingsFolderReader

async def main():
    reader = CastingsFolderReader()
    try:
        await reader.start()
        result = await reader.read_all_castings_channels(days_back={days}, limit_per_channel={limit})
        
        # Выводим результаты
        print("\\n" + "="*50)
        print("РЕЗУЛЬТАТЫ ЧТЕНИЯ КАНАЛОВ ИЗ ПАПКИ @CASTINGS")
        print("="*50)
        
        print(f"Всего каналов найдено: {{result['total_channels']}}")
        print(f"Всего сообщений прочитано: {{result['total_messages']}}")
        print(f"Дата чтения: {{result['read_date']}}")
        print(f"Период: {{result['days_back']}} дней назад")
        print(f"Лимит на канал: {{result['limit_per_channel']}} сообщений")
        
        # Сохраняем в базу данных
        all_messages = []
        for channel_data in result['channels']:
            all_messages.extend(channel_data['messages'])
        
        if all_messages:
            print(f"\\n💾 Сохранение {{len(all_messages)}} сообщений в базу данных...")
            saved = await reader.save_to_database(all_messages)
            if saved:
                print("✅ Сообщения успешно сохранены в ClickHouse")
            else:
                print("⚠️ Не удалось сохранить в базу данных")
        
        # Обновляем конфигурацию
        if result['channels']:
            print(f"\\n📝 Обновление конфигурации каналов...")
            channels_info = [ch['channel_info'] for ch in result['channels']]
            config_updated = reader.update_channels_config(channels_info)
            if config_updated:
                print("✅ Конфигурация каналов обновлена")
            else:
                print("⚠️ Не удалось обновить конфигурацию")
        
    finally:
        await reader.stop()

if __name__ == '__main__':
    asyncio.run(main())
"""
        
        # Записываем временный скрипт
        temp_file = 'temp_castings_reader.py'
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(temp_script)
        
        try:
            result = subprocess.run([sys.executable, temp_file], 
                                  capture_output=True, text=True, check=True)
            click.echo(result.stdout)
            click.echo("✅ Чтение каналов из папки @castings завершено успешно!")
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Ошибка при чтении каналов: {e}")
        if e.stderr:
            click.echo(f"Ошибка: {e.stderr}")
    except Exception as e:
        click.echo(f"❌ Неожиданная ошибка: {e}")

@root.group()
def bot():
    """Управление ботом"""
    pass

@bot.command()
def run():
    """Запустить основного бота"""
    click.echo("🤖 Запуск основного бота...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'main.py'], 
                              capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        click.echo("✅ Бот завершен успешно!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Ошибка при запуске бота: {e}")
        if e.stderr:
            click.echo(f"Ошибка: {e.stderr}")

@bot.command()
def group_responder():
    """Запустить групповой ответчик"""
    click.echo("👥 Запуск группового ответчика...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'scripts/run_group_responder.py'], 
                              capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        click.echo("✅ Групповой ответчик завершен успешно!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Ошибка при запуске группового ответчика: {e}")
        if e.stderr:
            click.echo(f"Ошибка: {e.stderr}")

@bot.command()
def docker():
    """Запустить в Docker"""
    click.echo("🐳 Запуск в Docker...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'scripts/main_docker.py'], 
                              capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        click.echo("✅ Docker запуск завершен успешно!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Ошибка при запуске в Docker: {e}")
        if e.stderr:
            click.echo(f"Ошибка: {e.stderr}")

@root.group()
def system():
    """Системные команды"""
    pass

@system.command()
def install():
    """Установить зависимости"""
    click.echo("📦 Установка зависимостей...")
    try:
        import subprocess
        result = subprocess.run(['bash', '-c', 'source venv/bin/activate && pip install -r requirements.txt'], 
                              capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        click.echo("✅ Зависимости установлены успешно!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Ошибка при установке зависимостей: {e}")
        if e.stderr:
            click.echo(f"Ошибка: {e.stderr}")

@system.command()
def docker_up():
    """Запустить Docker контейнеры"""
    click.echo("🐳 Запуск Docker контейнеров...")
    try:
        import subprocess
        result = subprocess.run(['docker-compose', 'up', '-d'], 
                              capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        click.echo("✅ Docker контейнеры запущены успешно!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Ошибка при запуске Docker контейнеров: {e}")
        if e.stderr:
            click.echo(f"Ошибка: {e.stderr}")

@system.command()
def docker_down():
    """Остановить Docker контейнеры"""
    click.echo("🛑 Остановка Docker контейнеров...")
    try:
        import subprocess
        result = subprocess.run(['docker-compose', 'down'], 
                              capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        click.echo("✅ Docker контейнеры остановлены успешно!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Ошибка при остановке Docker контейнеров: {e}")
        if e.stderr:
            click.echo(f"Ошибка: {e.stderr}")

@system.command()
def logs():
    """Показать логи"""
    click.echo("📋 Показ логов...")
    try:
        import subprocess
        result = subprocess.run(['docker-compose', 'logs', '-f'], 
                              capture_output=True, text=True, check=True)
        click.echo(result.stdout)
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Ошибка при показе логов: {e}")
        if e.stderr:
            click.echo(f"Ошибка: {e.stderr}")

@system.command()
def status():
    """Показать статус системы"""
    click.echo("📊 Статус системы...")
    try:
        import subprocess
        result = subprocess.run(['docker-compose', 'ps'], 
                              capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        click.echo("✅ Статус показан успешно!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Ошибка при показе статуса: {e}")
        if e.stderr:
            click.echo(f"Ошибка: {e.stderr}")

@system.command()
def database():
    """Управление базой данных ClickHouse"""
    click.echo("🗄️ Управление базой данных ClickHouse...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'scripts/manage_database.py'], 
                              capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        click.echo("✅ Управление базой данных завершено успешно!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Ошибка при управлении базой данных: {e}")
        if e.stderr:
            click.echo(f"Ошибка: {e.stderr}")

@system.command()
def clean_duplicates():
    """Очистка дублей в базе данных ClickHouse"""
    click.echo("🧹 Очистка дублей в ClickHouse...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'scripts/clean_duplicates.py'], 
                              capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        click.echo("✅ Очистка дублей завершена успешно!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Ошибка при очистке дублей: {e}")
        if e.stderr:
            click.echo(f"Ошибка: {e.stderr}")

if __name__ == '__main__':
    root()