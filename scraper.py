import feedparser
import requests
from bs4 import BeautifulSoup
import sqlite3

SOURCES = {
    'Habr': 'https://habr.com/ru/rss/articles/',
    'Lenta': 'https://lenta.ru/rss/',
    'BBC': 'http://feeds.bbci.co.uk/news/rss.xml'
}

def init_db():
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            description TEXT,
            publish_date TEXT,
            source TEXT,
            category TEXT DEFAULT 'uncategorized'
        )
    ''')
    conn.commit()
    conn.close()

def save_article(article_data):
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO articles (title, url, description, publish_date, source)
            VALUES (?, ?, ?, ?, ?)
        ''', article_data)
        conn.commit()
    except sqlite3.Error:
        pass
    finally:
        conn.close()

def fetch_news():
    all_news = []
    for source_name, url in SOURCES.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                desc = ""
                if 'summary' in entry:
                    desc = BeautifulSoup(entry.summary, "html.parser").get_text()
                
                article = (
                    entry.title,
                    entry.link,
                    desc[:500],
                    entry.published if 'published' in entry else "Unknown",
                    source_name
                )
                all_news.append(article)
        except Exception as e:
            print(f"Error skipping {source_name}: {e}")
    return all_news

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
    
    news_list = fetch_news()
    print(f"Found {len(news_list)} articles. Saving...")
    
    for article in news_list:
        save_article(article)
        
    print("Done. Check news.db file.")