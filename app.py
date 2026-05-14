"""
app.py — Flask приложение: Часть 3
Главная страница, поиск, фильтр по категориям, Dark Mode
"""

from flask import Flask, render_template, request, jsonify, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'news-aggregator-secret-2024'

DB_PATH = 'news.db'


def get_db():
    """Подключение к БД."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Создать таблицу articles если не существует."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            description TEXT,
            publish_date TEXT,
            source TEXT,
            category TEXT DEFAULT 'uncategorized',
            views INTEGER DEFAULT 0
        )
    ''')
    # Добавить колонку views если её нет
    try:
        conn.execute('ALTER TABLE articles ADD COLUMN views INTEGER DEFAULT 0')
    except Exception:
        pass
    conn.commit()
    conn.close()
    print('[✓] Database ready')


# ── Главная страница ──────────────────────────────────────────────────────────
@app.route('/')
def index():
    """
    Главная страница новостного агрегатора.
    Поддерживает фильтрацию по категории и поиск по ключевому слову.
    """
    conn = get_db()

    category = request.args.get('category', '')
    search   = request.args.get('q', '').strip()
    is_dark  = session.get('dark_mode', True)

    # ── Основной запрос ───────────────────────────────────────────────────────
    if category and search:
        rows = conn.execute(
            '''SELECT * FROM articles
               WHERE category = ?
               AND (title LIKE ? OR description LIKE ?)
               ORDER BY id DESC LIMIT 50''',
            (category, f'%{search}%', f'%{search}%')
        ).fetchall()

    elif category:
        rows = conn.execute(
            '''SELECT * FROM articles
               WHERE category = ?
               ORDER BY id DESC LIMIT 50''',
            (category,)
        ).fetchall()

    elif search:
        rows = conn.execute(
            '''SELECT * FROM articles
               WHERE title LIKE ? OR description LIKE ?
               ORDER BY id DESC LIMIT 50''',
            (f'%{search}%', f'%{search}%')
        ).fetchall()

    else:
        rows = conn.execute(
            'SELECT * FROM articles ORDER BY id DESC LIMIT 50'
        ).fetchall()

    rows = [dict(r) for r in rows]

    # ── Статистика по категориям ──────────────────────────────────────────────
    cat_stats = {}
    for cat in ['sport', 'politics', 'technology', 'gaming', 'uncategorized']:
        count = conn.execute(
            'SELECT COUNT(*) FROM articles WHERE category = ?', (cat,)
        ).fetchone()[0]
        cat_stats[cat] = count

    # ── Топ-5 по просмотрам (Тренды) ─────────────────────────────────────────
    trends = conn.execute(
        '''SELECT id, title, views, category
           FROM articles
           ORDER BY views DESC LIMIT 5'''
    ).fetchall()
    trends = [dict(t) for t in trends]

    # ── Общая статистика ──────────────────────────────────────────────────────
    total = conn.execute('SELECT COUNT(*) FROM articles').fetchone()[0]

    conn.close()

    return render_template(
        'index.html',
        news=rows,
        cat_stats=cat_stats,
        trends=trends,
        total=total,
        current_category=category,
        search_query=search,
        is_dark=is_dark
    )


# ── Страница одной статьи ─────────────────────────────────────────────────────
@app.route('/article/<int:article_id>')
def article(article_id):
    """Карточка статьи. Увеличивает счётчик просмотров."""
    conn = get_db()

    # Увеличить views
    conn.execute(
        'UPDATE articles SET views = views + 1 WHERE id = ?',
        (article_id,)
    )
    conn.commit()

    art = conn.execute(
        'SELECT * FROM articles WHERE id = ?', (article_id,)
    ).fetchone()
    conn.close()

    if art is None:
        return '<h2>Статья не найдена</h2><a href="/">← Назад</a>', 404

    is_dark = session.get('dark_mode', True)
    return render_template(
        'article.html',
        article=dict(art),
        is_dark=is_dark
    )


# ── Dark Mode переключение ────────────────────────────────────────────────────
@app.route('/toggle-dark')
def toggle_dark():
    """Переключить тёмную тему."""
    session['dark_mode'] = not session.get('dark_mode', True)
    return jsonify({'dark': session['dark_mode']})


# ── REST API: список новостей ─────────────────────────────────────────────────
@app.route('/api/news')
def api_news():
    """
    REST API endpoint — возвращает JSON список статей.
    Параметры: ?category=sport&limit=10
    """
    conn = get_db()
    category = request.args.get('category', '')
    limit    = min(int(request.args.get('limit', 20)), 100)

    if category:
        rows = conn.execute(
            'SELECT * FROM articles WHERE category=? ORDER BY id DESC LIMIT ?',
            (category, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            'SELECT * FROM articles ORDER BY id DESC LIMIT ?', (limit,)
        ).fetchall()

    conn.close()
    return jsonify([dict(r) for r in rows])


# ── REST API: тренды ──────────────────────────────────────────────────────────
@app.route('/api/trending')
def api_trending():
    """REST API — топ-5 самых просматриваемых статей."""
    conn = get_db()
    rows = conn.execute(
        '''SELECT id, title, views, category, source
           FROM articles ORDER BY views DESC LIMIT 5'''
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ── Запуск ────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    # 1. Инициализация БД
    init_db()

    # 2. Запуск скрапера если БД пустая
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute('SELECT COUNT(*) FROM articles').fetchone()[0]
    conn.close()

    if count == 0:
        print('[i] БД пустая — запускаю скрапер...')
        try:
            from scraper import fetch_news, save_article
            news_list = fetch_news()
            for art in news_list:
                save_article(art)
            print(f'[✓] Загружено {len(news_list)} статей')
        except Exception as e:
            print(f'[!] Ошибка скрапера: {e}')

    # 3. Классификация если есть uncategorized
    try:
        from classifier import classify_articles_in_db
        classify_articles_in_db(DB_PATH)
    except Exception as e:
        print(f'[!] Классификатор: {e}')

    # 4. Запуск scheduler
    try:
        from scheduler import start_scheduler
        start_scheduler()
    except Exception as e:
        print(f'[!] Scheduler: {e}')

    # 5. Flask
    app.run(debug=True, port=5001, host='0.0.0.0')