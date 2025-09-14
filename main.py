"""
Главный файл для запуска Telegram бота-автоответчика
"""
import asyncio
import sys
import os
import argparse

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.bot_manager import bot_manager
from src.config.logging_config import setup_logging, get_logger

# Настраиваем логирование
setup_logging(level="INFO", log_to_file=True)
logger = get_logger("main")


def parse_arguments():
    """Парсит аргументы командной строки"""
    parser = argparse.ArgumentParser(
        description="Telegram бот-автоответчик",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py                    # Интерактивный выбор
  python main.py --bot smart        # Умный автоответчик
  python main.py --bot simple       # Простой автоответчик
  python main.py --bot group        # Групповой автоответчик
  python main.py --list             # Показать доступные боты
  python main.py --list-groups      # Показать доступные группы
        """
    )
    
    parser.add_argument(
        '--bot', '-b',
        choices=['smart', 'simple', 'group'],
        help='Тип бота для запуска'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='Показать список доступных ботов'
    )
    
    parser.add_argument(
        '--list-groups', '-g',
        action='store_true',
        help='Показать список доступных групп (для группового бота)'
    )
    
    return parser.parse_args()


async def main():
    """Главная функция для запуска автоответчика"""
    args = parse_arguments()
    
    # Если запрошен список ботов
    if args.list:
        print("\n🤖 Доступные типы ботов:")
        bot_manager.list_available_bots()
        return
    
    # Если запрошен список групп
    if args.list_groups:
        print("\n🔍 Поиск доступных групп...")
        try:
            from src.bots.group_responder import GroupResponder
            bot = GroupResponder()
            await bot.start()
            await bot.list_available_groups()
            await bot.stop()
        except Exception as e:
            logger.error(f"Ошибка при получении списка групп: {e}")
        return
    
    # Если указан конкретный бот
    if args.bot:
        logger.info(f"Запуск {args.bot} автоответчика")
        await bot_manager.run_bot(args.bot)
        return
    
    # Интерактивный режим
    logger.info("Запуск Telegram бота-автоответчика")
    print("\n🤖 Доступные типы ботов:")
    bot_manager.list_available_bots()
    
    while True:
        try:
            print("\nВыберите тип бота:")
            print("1. Smart Responder (умный автоответчик)")
            print("2. Simple Responder (простой автоответчик)")
            print("3. Group Responder (групповой автоответчик)")
            print("0. Выход")
            
            choice = input("\nВведите номер (0-3): ").strip()
            
            if choice == '0':
                print("👋 До свидания!")
                return
            elif choice == '1':
                logger.info("Запуск умного автоответчика")
                await bot_manager.run_bot('smart')
                break
            elif choice == '2':
                logger.info("Запуск простого автоответчика")
                await bot_manager.run_bot('simple')
                break
            elif choice == '3':
                logger.info("Запуск группового автоответчика")
                await bot_manager.run_bot('group')
                break
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
                
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            return
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            print(f"❌ Произошла ошибка: {e}")
            return


async def run_smart_responder():
    """Запуск умного автоответчика"""
    logger.info("Запуск умного автоответчика")
    await bot_manager.run_bot('smart')


async def run_simple_responder():
    """Запуск простого автоответчика"""
    logger.info("Запуск простого автоответчика")
    await bot_manager.run_bot('simple')


async def run_group_responder():
    """Запуск группового автоответчика"""
    logger.info("Запуск группового автоответчика")
    await bot_manager.run_bot('group')


# Универсальный запуск
if __name__ == "__main__":
    try:
        # Если уже есть event loop (Jupyter), используем await
        loop = asyncio.get_running_loop()
        # В Jupyter раскомментируйте нужную строку:
        # await run_smart_responder()
        # await run_simple_responder()
        # await run_group_responder()
        # await main()
    except RuntimeError:
        # Если нет event loop (обычный Python), создаем новый
        asyncio.run(main())