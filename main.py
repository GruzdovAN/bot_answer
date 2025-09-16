#!/usr/bin/env python3
"""
Простой запуск универсального скрапера
"""

import asyncio
import logging
from src.core.universal_scraper import UniversalScraper

async def main():
    """Основная функция"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    scraper = UniversalScraper()
    
    try:
        await scraper.client.start()
        await scraper.scrape_all_channels()
    finally:
        await scraper.client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())