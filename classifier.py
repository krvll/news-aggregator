"""
classifier.py — Часть 2: ML классификатор новостей

"""

import os
import re
import pickle
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ── Датасет (расширь при необходимости) ──────────────────────────────────────
TRAINING_DATA = [
    # Спорт
    ("Футбольный матч завершился победой со счётом 3:1", "sport"),
    ("Сборная выиграла чемпионат мира по хоккею", "sport"),
    ("Теннисист вышел в финал турнира Большого шлема", "sport"),
    ("Боксёр нокаутировал соперника в третьем раунде", "sport"),
    ("Баскетбольная команда установила рекорд сезона", "sport"),
    ("Олимпийские игры открылись торжественной церемонией", "sport"),
    ("Атлет побил мировой рекорд в беге на 100 метров", "sport"),
    ("Гонщик Формулы 1 занял поул-позицию на квалификации", "sport"),
    ("Клуб подписал контракт с новым нападающим", "sport"),
    ("Волейбольная команда вышла в плей-офф чемпионата", "sport"),
    ("Хоккеист забил победный гол в овертайме", "sport"),
    ("Чемпион по борьбе защитил свой титул", "sport"),
    ("Марафонец финишировал первым с личным рекордом", "sport"),
    ("Тренер сборной объявил состав на чемпионат", "sport"),
    ("Спортсмен получил золотую медаль на Олимпиаде", "sport"),
    ("Футбольный клуб выиграл Лигу чемпионов", "sport"),
    ("Пловец установил новый мировой рекорд", "sport"),
    ("Команда выиграла серию плей-офф 4-2", "sport"),
    ("Лыжник стал чемпионом мира в слаломе", "sport"),
    ("Велогонщик финишировал первым на Тур де Франс", "sport"),
    ("Футболист оформил хет-трик в матче лиги", "sport"),
    ("Нападающий забил гол в добавленное время матча", "sport"),
    ("Игрок оформил дубль в финальном матче турнира", "sport"),
    ("Вчерашний матч завершился разгромной победой", "sport"),
    ("Форвард стал лучшим игроком недели", "sport"),

    # Политика
    ("Президент подписал новый закон об экономике", "politics"),
    ("Правительство объявило о реформе образования", "politics"),
    ("Переговоры между странами завершились соглашением", "politics"),
    ("Министр иностранных дел встретился с послом", "politics"),
    ("Парламент проголосовал за новый бюджет страны", "politics"),
    ("Выборы в сенат пройдут в следующем месяце", "politics"),
    ("Лидеры G7 обсудили международную безопасность", "politics"),
    ("Санкции против страны были расширены", "politics"),
    ("Конституционный суд вынес решение по делу", "politics"),
    ("Премьер-министр выступил с ежегодным посланием", "politics"),
    ("Дипломаты подписали мирное соглашение", "politics"),
    ("Правительство ввело новые налоговые льготы", "politics"),
    ("Оппозиция потребовала отставки министра", "politics"),
    ("Президент встретился с лидерами других государств", "politics"),
    ("Парламент принял поправки к конституции", "politics"),
    ("Страна вступила в международную организацию", "politics"),
    ("Референдум по вопросу независимости прошёл успешно", "politics"),
    ("Посол был вызван в министерство иностранных дел", "politics"),
    ("Новый закон о труде вступил в силу", "politics"),
    ("Правительство объявило чрезвычайное положение", "politics"),

    # Технологии
    ("Apple представила новый iPhone с улучшенной камерой", "technology"),
    ("Искусственный интеллект научился писать программный код", "technology"),
    ("Стартап привлёк миллиард долларов инвестиций в ИИ", "technology"),
    ("Новый процессор AMD превосходит Intel по производительности", "technology"),
    ("Квантовый компьютер решил задачу за секунды", "technology"),
    ("Tesla выпустила обновление автопилота", "technology"),
    ("SpaceX успешно запустила ракету на орбиту", "technology"),
    ("Google обновил алгоритм поиска", "technology"),
    ("Нейросеть создала реалистичное изображение за секунды", "technology"),
    ("Новый язык программирования стал популярнее Python", "technology"),
    ("Microsoft выпустила новую версию Windows", "technology"),
    ("Учёные создали робота способного ходить по лестнице", "technology"),
    ("Смартфон нового поколения получил складной экран", "technology"),
    ("Компания запустила спутниковый интернет в новых регионах", "technology"),
    ("Разработчики представили браузер с встроенным ИИ", "technology"),
    ("Вышла новая версия популярного фреймворка", "technology"),
    ("Учёные разработали аккумулятор с зарядкой за минуту", "technology"),
    ("Компания открыла исходный код своей модели ИИ", "technology"),
    ("Новый чип обеспечивает работу без подключения к сети", "technology"),
    ("Технологический гигант объявил о поглощении стартапа", "technology"),

    # Gaming
    ("Вышло долгожданное продолжение игры GTA", "gaming"),
    ("Игроки установили рекорд по просмотрам на Twitch", "gaming"),
    ("Новая видеокарта обеспечивает 4K при 120 FPS", "gaming"),
    ("Турнир по Dota 2 собрал миллионный призовой фонд", "gaming"),
    ("PlayStation 6 будет выпущена в следующем году", "gaming"),
    ("Разработчики анонсировали новое DLC для популярной игры", "gaming"),
    ("Киберспортивная команда выиграла мировой чемпионат", "gaming"),
    ("Nintendo выпустила новую консоль с улучшенным экраном", "gaming"),
    ("Онлайн-игра достигла 10 миллионов активных игроков", "gaming"),
    ("Steam объявил о рекордных продажах в этом квартале", "gaming"),
    ("Игровая студия анонсировала ролевую игру открытого мира", "gaming"),
    ("Чемпионат по CS2 пройдёт в следующем месяце", "gaming"),
    ("Разработчики исправили критический баг в патче", "gaming"),
    ("Xbox Game Pass получил новые игры в каталог", "gaming"),
    ("Игра получила награду лучшей игры года", "gaming"),
    ("Speedrunner побил мировой рекорд прохождения", "gaming"),
    ("Стриммер собрал миллион подписчиков за месяц", "gaming"),
    ("Выживальческая игра стала хитом сезона", "gaming"),
    ("VR-игра получила восторженные отзывы критиков", "gaming"),
    ("Мобильная игра заработала миллиард за первый месяц", "gaming"),
    ("Minecraft получил крупнейшее обновление с новыми биомами", "gaming"),
    ("В Minecraft добавили нового моба и механики крафта", "gaming"),
]


# ── Очистка текста ────────────────────────────────────────────────────────────
def clean_text(text: str) -> str:
    """Убирает лишние символы, приводит к нижнему регистру."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)   
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ── Обучение модели ───────────────────────────────────────────────────────────
def train_model(save_path: str = "models/classifier.pkl") -> Pipeline:
    """
    Обучает Pipeline: TfidfVectorizer → LogisticRegression.
    Сохраняет модель в файл и возвращает её.
    """
    texts, labels = zip(*TRAINING_DATA)
    texts = [clean_text(t) for t in texts]

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.15, random_state=42
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),  
            min_df=1,
            max_features=5000,
        )),
        ("clf", LogisticRegression(max_iter=1000, C=1.0)),
    ])

    pipeline.fit(X_train, y_train)

    # Метрики
    y_pred = pipeline.predict(X_test)
    print("=== Отчёт о качестве модели ===")
    print(classification_report(y_test, y_pred, zero_division=0))

    # Сохранение
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"[✓] Модель сохранена: {save_path}")

    return pipeline


# ── Загрузка модели ───────────────────────────────────────────────────────────
def load_model(path: str = "models/classifier.pkl") -> Pipeline:
    """Загружает сохранённую модель из файла."""
    if not os.path.exists(path):
        print("[!] Модель не найдена, запускаю обучение...")
        return train_model(path)
    with open(path, "rb") as f:
        return pickle.load(f)


# ── Предсказание категории ────────────────────────────────────────────────────
def predict_category(text: str, model: Pipeline | None = None) -> str:
    """Возвращает предсказанную категорию для текста."""
    if model is None:
        model = load_model()
    cleaned = clean_text(text)
    return model.predict([cleaned])[0]


# ── Классификация статей из БД ────────────────────────────────────────────────
def classify_articles_in_db(db_path: str = "data/news.db"):
    """
    Читает статьи без категории из БД, предсказывает и записывает категорию.
    Добавляет колонку category в таблицу articles, если её нет.
    """
    model = load_model()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Добавить колонку category, если её нет
    cursor.execute("PRAGMA table_info(articles)")
    columns = [row[1] for row in cursor.fetchall()]
    if "category" not in columns:
        cursor.execute("ALTER TABLE articles ADD COLUMN category TEXT DEFAULT 'unknown'")
        conn.commit()

    # Получаем статьи без категории
    cursor.execute("SELECT id, title, description FROM articles WHERE category IS NULL OR category = 'unknown'")
    rows = cursor.fetchall()

    if not rows:
        print("[i] Нет статей для классификации.")
        conn.close()
        return

    for row_id, title, description in rows:
        text = f"{title} {description or ''}"
        category = predict_category(text, model)
        cursor.execute("UPDATE articles SET category = ? WHERE id = ?", (category, row_id))
        print(f"[{row_id}] {title[:50]}... → {category}")

    conn.commit()
    conn.close()
    print(f"[✓] Классифицировано {len(rows)} статей.")


# ── Точка входа ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Обучение классификатора ===")
    model = train_model()

    print("\n=== Тест предсказания ===")
    test_headlines = [
    "Месси оформил хет-трик в вчерашнем матче",
    "Новый закон об экономической безопасности принят",
    "OpenAI выпустила новую версию GPT",
    "Финал чемпионата мира по футболу состоится в декабре",
    "Minecraft получил крупнейшее обновление года",
    ]
    for headline in test_headlines:
        cat = predict_category(headline, model)
        print(f"  [{cat}] {headline}")