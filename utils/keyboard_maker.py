from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_time_choice_keyboard():
    """
    Create keyboard for choosing time input method
    """
    keyboard = [
        [
            InlineKeyboardButton("Конкретний час", callback_data="time_type:specific"),
            InlineKeyboardButton("Через проміжок часу", callback_data="time_type:delay")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_reminder_management_keyboard(reminder_id: int):
    """
    Create keyboard for managing existing reminder
    """
    keyboard = [
        [
            InlineKeyboardButton("Видалити", callback_data=f"delete_reminder:{reminder_id}"),
            InlineKeyboardButton("Відкласти", callback_data=f"snooze_reminder:{reminder_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirmation_keyboard(action: str, reminder_id: int):
    """
    Create confirmation keyboard
    """
    keyboard = [
        [
            InlineKeyboardButton("Так", callback_data=f"confirm_{action}:{reminder_id}"),
            InlineKeyboardButton("Ні", callback_data=f"cancel_{action}:{reminder_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)