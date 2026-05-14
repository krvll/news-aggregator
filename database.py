import sqlite3

def init_db():
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT None,
            url TEXT UNIQUE NOT None,
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
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()