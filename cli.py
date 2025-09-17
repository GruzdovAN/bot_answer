#!/usr/bin/env python3
"""
CLI для управления Telegram Bot проектом
"""

import asyncio
import os
import sys
import subprocess
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
    - llm: управление LLM (Large Language Model)
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
def llm():
    """Управление LLM (Large Language Model)"""
    pass

@llm.command()
@click.option('--message', '-m', required=True, help='Текст сообщения для обработки')
@click.option('--model', default='deepseek-chat', help='Модель для обработки (по умолчанию: deepseek-chat)')
@click.option('--output', '-o', help='Файл для сохранения результата (JSON)')
@click.option('--verbose', '-v', is_flag=True, help='Подробный вывод')
def process_message(message, model, output, verbose):
    """Обработать сообщение через LLM для извлечения информации о кастинге"""
    click.echo("🤖 Обработка сообщения через LLM...")
    
    try:
        # Импортируем функцию обработки
        from src.llm.deepseek import process_telegram_message
        
        if verbose:
            click.echo(f"📝 Сообщение: {message[:100]}{'...' if len(message) > 100 else ''}")
            click.echo(f"🧠 Модель: {model}")
        
        # Обрабатываем сообщение
        result = process_telegram_message(message, model)
        
        if result['success']:
            click.echo("✅ Сообщение успешно обработано!")
            
            if verbose:
                click.echo(f"📊 Тип сообщения: {result['extracted_data'].get('message_type', 'N/A')}")
                click.echo(f"🎬 Тип кастинга: {result['extracted_data'].get('casting_type', 'N/A')}")
                click.echo(f"👥 Количество актеров: {len(result['extracted_data'].get('actors', []))}")
                click.echo(f"💰 Стоимость обработки: ${result['cost_info'].get('total_cost_usd', 'N/A')}")
            
            # Сохраняем результат в файл если указан
            if output:
                import json
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                click.echo(f"💾 Результат сохранен в файл: {output}")
            
            # Показываем краткую информацию об актерах
            if result['extracted_data'] and 'actors' in result['extracted_data']:
                actors = result['extracted_data']['actors']
                if actors:
                    click.echo(f"\n👥 Найдено актеров: {len(actors)}")
                    for i, actor in enumerate(actors[:3], 1):  # Показываем первых 3
                        click.echo(f"  {i}. {actor.get('gender', 'N/A')}, {actor.get('age_range', 'N/A')} - {actor.get('role_features', 'N/A')}")
                    if len(actors) > 3:
                        click.echo(f"  ... и еще {len(actors) - 3} актеров")
        else:
            click.echo(f"❌ Ошибка при обработке: {result.get('error', 'Неизвестная ошибка')}")
            
    except ImportError as e:
        click.echo(f"❌ Ошибка импорта: {e}")
        click.echo("Убедитесь, что модуль src.llm.deepseek доступен")
    except Exception as e:
        click.echo(f"❌ Неожиданная ошибка: {e}")

@llm.command()
@click.option('--model', default='deepseek-chat', help='Модель для тестирования')
def test(model):
    """Тестировать LLM с примером сообщения о кастинге"""
    click.echo("🧪 Тестирование LLM...")
    
    try:
        # Запускаем тестовый файл
        import subprocess
        result = subprocess.run([sys.executable, 'src/llm/test_deepseek.py'], 
                              capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        click.echo("✅ Тестирование LLM завершено успешно!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Ошибка при тестировании LLM: {e}")
        if e.stderr:
            click.echo(f"Ошибка: {e.stderr}")

@llm.command()
@click.option('--input', '-i', required=True, help='Файл с сообщениями (по одному на строку)')
@click.option('--output', '-o', required=True, help='Файл для сохранения результатов (JSON)')
@click.option('--model', default='deepseek-chat', help='Модель для обработки')
@click.option('--batch-size', default=5, help='Размер пакета для обработки')
def batch_process(input, output, model, batch_size):
    """Пакетная обработка сообщений из файла"""
    click.echo(f"📦 Пакетная обработка сообщений из файла {input}...")
    
    try:
        from src.llm.deepseek import process_telegram_message
        import json
        import time
        
        # Читаем сообщения из файла
        with open(input, 'r', encoding='utf-8') as f:
            messages = [line.strip() for line in f if line.strip()]
        
        click.echo(f"📝 Найдено {len(messages)} сообщений для обработки")
        
        results = []
        total_cost = 0
        
        # Обрабатываем сообщения пакетами
        for i in range(0, len(messages), batch_size):
            batch = messages[i:i + batch_size]
            click.echo(f"🔄 Обработка пакета {i//batch_size + 1}/{(len(messages) + batch_size - 1)//batch_size}...")
            
            for j, message in enumerate(batch):
                click.echo(f"  📝 Сообщение {i + j + 1}/{len(messages)}")
                
                try:
                    result = process_telegram_message(message, model)
                    results.append(result)
                    
                    if result['cost_info']:
                        total_cost += result['cost_info'].get('total_cost_usd', 0)
                    
                    # Небольшая пауза между запросами
                    time.sleep(0.5)
                    
                except Exception as e:
                    click.echo(f"    ❌ Ошибка: {e}")
                    results.append({
                        'success': False,
                        'original_message': message,
                        'error': str(e)
                    })
            
            # Пауза между пакетами
            if i + batch_size < len(messages):
                click.echo("⏳ Пауза между пакетами...")
                time.sleep(2)
        
        # Сохраняем результаты
        with open(output, 'w', encoding='utf-8') as f:
            json.dump({
                'total_messages': len(messages),
                'processed_messages': len(results),
                'total_cost_usd': round(total_cost, 6),
                'model_used': model,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'results': results
            }, f, ensure_ascii=False, indent=2)
        
        click.echo(f"✅ Пакетная обработка завершена!")
        click.echo(f"📊 Обработано: {len(results)}/{len(messages)} сообщений")
        click.echo(f"💰 Общая стоимость: ${round(total_cost, 6)}")
        click.echo(f"💾 Результаты сохранены в: {output}")
        
    except FileNotFoundError:
        click.echo(f"❌ Файл {input} не найден")
    except Exception as e:
        click.echo(f"❌ Ошибка при пакетной обработке: {e}")

@llm.command()
@click.option('--days', default=1, help='Количество дней назад для чтения сообщений')
@click.option('--limit', default=10, help='Лимит сообщений для обработки')
@click.option('--model', default='deepseek-chat', help='Модель для обработки')
@click.option('--output', '-o', help='Файл для сохранения результатов (JSON)')
def process_recent(days, limit, model, output):
    """Обработать недавние сообщения из базы данных через LLM"""
    click.echo(f"🔄 Обработка недавних сообщений ({days} дней назад, лимит: {limit})...")
    
    try:
        # Создаем временный скрипт для обработки
        temp_script = f"""
import asyncio
import sys
import os
import json
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm.deepseek import process_telegram_message
from database.clickhouse_client import ClickHouseClient

async def main():
    client = ClickHouseClient()
    results = []
    total_cost = 0
    
    try:
        # Получаем недавние сообщения
        messages = await client.get_recent_messages(days_back={days}, limit={limit})
        print(f"Найдено {{len(messages)}} сообщений для обработки")
        
        for i, message in enumerate(messages, 1):
            print(f"Обработка сообщения {{i}}/{{len(messages)}}")
            
            try:
                result = process_telegram_message(message['text'], '{model}')
                result['message_id'] = message['id']
                result['channel_id'] = message['channel_id']
                result['date'] = message['date']
                results.append(result)
                
                if result['cost_info']:
                    total_cost += result['cost_info'].get('total_cost_usd', 0)
                
                # Пауза между запросами
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Ошибка при обработке сообщения {{i}}: {{e}}")
                results.append({{
                    'success': False,
                    'message_id': message['id'],
                    'original_message': message['text'],
                    'error': str(e)
                }})
        
        # Сохраняем результаты
        output_data = {{
            'total_messages': len(messages),
            'processed_messages': len(results),
            'total_cost_usd': round(total_cost, 6),
            'model_used': '{model}',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'results': results
        }}
        
        if '{output}':
            with open('{output}', 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            print(f"Результаты сохранены в {{'{output}'}}")
        
        print(f"Обработано: {{len(results)}}/{{len(messages)}} сообщений")
        print(f"Общая стоимость: ${{round(total_cost, 6)}}")
        
    finally:
        await client.close()

if __name__ == '__main__':
    asyncio.run(main())
"""
        
        # Записываем временный скрипт
        temp_file = 'temp_llm_processor.py'
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(temp_script)
        
        try:
            result = subprocess.run([sys.executable, temp_file], 
                                  capture_output=True, text=True, check=True)
            click.echo(result.stdout)
            click.echo("✅ Обработка недавних сообщений завершена успешно!")
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
    except Exception as e:
        click.echo(f"❌ Ошибка при обработке недавних сообщений: {e}")

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