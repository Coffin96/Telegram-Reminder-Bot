from typing import Dict, Optional
import os
from dotenv import load_dotenv
import sys

class Config:
    """Configuration class for the reminder bot"""
    BOT_TOKEN: Optional[str] = None
    DATABASE_URL: str = 'sqlite:///reminder_bot.db'
    DEFAULT_TIMEZONE: str = 'Europe/Kiev'

    # Command list
    COMMANDS: Dict[str, str] = {
        'start': 'Почати роботу з ботом',
        'help': 'Показати довідку',
        'new': 'Створити нове нагадування',
        'list': 'Показати всі активні нагадування',
        'cancel': 'Скасувати поточну операцію'
    }

    # Message texts
    MESSAGES: Dict[str, str] = {
        'welcome': """Привіт! Я бот для нагадувань. 
Я можу допомогти вам не забути про важливі справи.

Використовуйте /new щоб створити нове нагадування.""",
        'help': """Доступні команди:
/new - Створити нове нагадування
/list - Показати всі активні нагадування
/cancel - Скасувати поточну операцію""",
        'reminder_text': 'Введіть текст нагадування:',
        'choose_time': 'Оберіть спосіб встановлення часу:',
        'enter_specific_time': 'Введіть час у форматі ГГ:ХХ ДД.ММ.РРРР',
        'enter_delay_time': 'Через скільки часу нагадати? (наприклад: 1г 30хв або 2 години)',
        'invalid_time': 'Невірний формат часу. Спробуйте ще раз.',
        'reminder_set': 'Нагадування встановлено на {}',
        'no_active_reminders': 'У вас немає активних нагадувань',
        'operation_cancelled': 'Операцію скасовано',
        'invalid_operation': 'Немає активних операцій для скасування.',
        'reminder_deleted': 'Нагадування видалено.',
        'reminder_not_found': 'Помилка: нагадування не знайдено.',
        'enter_snooze_time': 'На скільки часу відкласти нагадування?',
        'reminder_management': 'Що бажаєте зробити з цим нагадуванням?'
    }

    @classmethod
    def load_environment(cls) -> None:
        """Load environment variables from .env file"""
        try:
            load_dotenv(encoding='utf-8')
        except Exception as e:
            print(f"Error loading .env file: {e}")
            sys.exit(1)

        cls.BOT_TOKEN = os.getenv('BOT_TOKEN')
        if not cls.BOT_TOKEN:
            print("No BOT_TOKEN found in .env file")
            sys.exit(1)
        
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            cls.DATABASE_URL = db_url

# Load environment variables on module import
Config.load_environment()