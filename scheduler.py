"""
scheduler.py — APScheduler: автообновление новостей каждый час.
"""

from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = 'news.db'
scheduler = BackgroundScheduler(daemon=True)


def scrape_and_classify():
    """
    Главная задача планировщика:
    1. Собрать новые статьи через scraper
    2. Сохранить в SQLite
    3. Классифицировать через ML модель
    """
    logger.info('=== [Scheduler] Запуск обновления новостей ===')

    try:
        # Шаг 1: Скрапинг
        from scraper import fetch_news, save_article
        news_list = fetch_news()
        for art in news_list:
            save_article(art)
        logger.info(f'[Scheduler] Загружено статей: {len(news_list)}')

        # Шаг 2: Классификация новых статей
        from classifier import classify_articles_in_db
        classify_articles_in_db(DB_PATH)
        logger.info('[Scheduler] Классификация завершена')

    except Exception as e:
        logger.error(f'[Scheduler] Ошибка: {e}')
        import traceback
        traceback.print_exc()


def start_scheduler():
    """Запустить фоновый планировщик — обновление каждый час."""
    if not scheduler.running:
        scheduler.add_job(
            scrape_and_classify,
            'interval',
            hours=1,
            id='news_update',
            replace_existing=True
        )
        scheduler.start()
        logger.info('[✓] APScheduler запущен — обновление каждый час')


def stop_scheduler():
    """Остановить планировщик."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info('[✓] APScheduler остановлен')