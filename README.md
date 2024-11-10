# Telegram Reminder Bot

Бот для створення та управління нагадуваннями в Telegram.

## Функціональність

- Створення нових нагадувань
- Вибір часу двома способами:
  - Конкретний час (наприклад, "14:30")
  - Через проміжок часу (наприклад, "2 години 30 хвилин")
- Перегляд активних нагадувань
- Видалення нагадувань
- Відкладання нагадувань

## Встановлення

1. Клонуйте репозиторій:
```bash
git clone https://github.com/your-username/telegram-reminder-bot.git
cd telegram-reminder-bot
```

2. Створіть віртуальне середовище та активуйте його:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/MacOS
venv\Scripts\activate     # для Windows
```

3. Встановіть залежності:
```bash
pip install -r requirements.txt
```

4. Створіть файл `.env` та додайте наступні змінні:
```
BOT_TOKEN=your_bot_token_here
DATABASE_URL=sqlite:///reminder_bot.db  # або ваша URL для PostgreSQL
```

## Налаштування для Render.com

1. Створіть новий Web Service на Render.com
2. Вкажіть посилання на ваш GitHub репозиторій
3. Виберіть Python як Runtime Environment
4. Додайте змінні середовища (BOT_TOKEN)
5. Вкажіть команду для запуску:
```bash
python main.py
```

## Команди бота

- `/start` - Почати роботу з ботом
- `/help` - Показати довідку
- `/new` - Створити нове нагадування
- `/list` - Показати всі активні нагадування
- `/cancel` - Скасувати поточну операцію

## Розробка

Проект має модульну структуру:
- `main.py` - головний файл додатку
- `config.py` - конфігурація
- `database/` - робота з базою даних
- `handlers/` - обробники команд та повідомлень
- `utils/` - допоміжні функції

## Ліцензія

MIT