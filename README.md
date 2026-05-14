```markdown
# News Aggregator (Part 3) — Flask + SQLite + ML + APScheduler

Проект новостного агрегатора: приложение на **Flask** собирает новости из RSS, сохраняет в **SQLite**, классифицирует по категориям с помощью **ML-модели** (scikit-learn) и отображает в веб-интерфейсе. Обновление новостей выполняется автоматически каждый час через **APScheduler**.

---

## Возможности

- Сбор новостей из RSS-источников (`scraper.py`)
- Хранение статей в SQLite (`news.db`)
- ML-классификация по категориям: `sport / politics / technology / gaming` (`classifier.py`)
- Веб-интерфейс:
  - главная лента (последние 50)
  - поиск по заголовку и описанию (`q`)
  - фильтр по категории (`category`)
  - страница отдельной статьи + счётчик просмотров (`views`)
  - тёмная тема (Dark Mode) через сессию
- REST API:
  - `/api/news`
  - `/api/trending`
- Автообновление каждый час: скрапинг + классификация (`scheduler.py`)

---

## Структура проекта

```
part3/
├── app.py
├── classifier.py
├── database.py
├── scraper.py
├── scheduler.py
├── news.db
├── models/
│   └── classifier.pkl
├── templates/
│   ├── base.html
│   ├── index.html
│   └── article.html
└── static/
    └── style.css
```

---

## Установка и запуск

### 1) Создать и активировать окружение (рекомендуется)

```bash
python -m venv venv
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 2) Установить зависимости

```bash
pip install flask apscheduler scikit-learn feedparser beautifulsoup4 lxml requests
```

### 3) Запуск приложения

```bash
python app.py
```

По умолчанию сервер стартует на:

- `http://localhost:5001`

При старте `app.py` автоматически:
1. создаёт таблицу `articles` (если её нет)
2. если база пустая — запускает `scraper` и сохраняет статьи
3. запускает классификацию статей через `classifier.py`
4. запускает планировщик `APScheduler` (обновление каждый час)

---

## Веб-интерфейс (маршруты)

- **Главная:** `GET /`  
- **Поиск:** `GET /?q=python`
- **Фильтр по категории:** `GET /?category=technology`
- **Поиск + категория:** `GET /?category=sport&q=final`
- **Статья:** `GET /article/<id>` (увеличивает `views`)
- **Тёмная тема:** `GET /toggle-dark` (возвращает JSON)

---

## REST API

### Список новостей
`GET /api/news`

Параметры:
- `category` (опционально): `sport|politics|technology|gaming|uncategorized`
- `limit` (опционально, по умолчанию 20, максимум 100)

Пример:
`/api/news?category=gaming&limit=10`

### Тренды (топ-5 по просмотрам)
`GET /api/trending`

---

## База данных (SQLite)

Файл: `news.db`  
Таблица: `articles`

| Поле | Тип | Описание |
|---|---|---|
| `id` | INTEGER PK AUTOINCREMENT | идентификатор |
| `title` | TEXT NOT NULL | заголовок |
| `url` | TEXT UNIQUE NOT NULL | ссылка (защита от дублей) |
| `description` | TEXT | описание/краткий текст |
| `publish_date` | TEXT | дата публикации (как строка из RSS) |
| `source` | TEXT | источник (Habr/Lenta/BBC) |
| `category` | TEXT | категория (по умолчанию `uncategorized`) |
| `views` | INTEGER | просмотры (по умолчанию `0`) |

---

## Логика ML (classifier.py)

- Предобработка: `lower()`, удаление пунктуации, нормализация пробелов
- Модель: `TfidfVectorizer(ngram_range=(1,2))` + `LogisticRegression`
- Модель сохраняется в: `models/classifier.pkl`
- `classify_articles_in_db(db_path)` классифицирует статьи, у которых `category` пустая/`unknown` (в зависимости от схемы)

---

## Планировщик (scheduler.py)

`APScheduler BackgroundScheduler` раз в час запускает задачу:
1. `fetch_news()` → получение статей из RSS
2. `save_article()` → запись в SQLite (дубликаты игнорируются по `url`)
3. `classify_articles_in_db()` → классификация новых/неразмеченных статей

---

## Примечания

- В проекте есть `database.py` и также инициализация БД в `app.py`. Для работы приложения достаточно запускать `app.py`.
- SQLite подходит для небольшого проекта/учебной работы; при росте нагрузки рекомендуется PostgreSQL и вынос фоновых задач в Celery/Redis.

---
```