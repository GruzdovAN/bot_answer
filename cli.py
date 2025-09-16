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

if __name__ == '__main__':
    root()