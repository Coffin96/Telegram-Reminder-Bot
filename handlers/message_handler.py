from telegram import Update
from telegram.ext import ContextTypes
from database.db_handler import DatabaseHandler
from utils.keyboard_maker import get_time_choice_keyboard
from utils.time_parser import parse_specific_time, parse_delay_time, format_reminder_time
from datetime import datetime
from config import MESSAGES
from typing import Optional, Dict, Any

# State constants
class States:
    WAITING_FOR_TEXT = 'waiting_for_reminder_text'
    CHOOSING_TIME_TYPE = 'waiting_for_time_choice'
    ENTERING_SPECIFIC_TIME = 'waiting_for_specific_time'
    ENTERING_DELAY_TIME = 'waiting_for_delay_time'

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    await update.message.reply_text(MESSAGES['welcome'])

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    await update.message.reply_text(MESSAGES['help'])

async def new_reminder_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle /new command"""
    context.user_data['state'] = States.WAITING_FOR_TEXT
    await update.message.reply_text(MESSAGES['reminder_text'])
    return States.WAITING_FOR_TEXT

async def handle_reminder_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle reminder text input"""
    context.user_data['reminder_text'] = update.message.text
    context.user_data['state'] = States.CHOOSING_TIME_TYPE
    await update.message.reply_text(
        MESSAGES['choose_time'],
        reply_markup=get_time_choice_keyboard()
    )
    return States.CHOOSING_TIME_TYPE

async def handle_time_input(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                          parse_func: callable) -> Optional[str]:
    """Generic handler for time input"""
    try:
        reminder_time = parse_func(update.message.text)
        await save_reminder(update, context, reminder_time)
        return None
    except ValueError:
        await update.message.reply_text(MESSAGES['invalid_time'])
        return context.user_data['state']

async def specific_time_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    """Handle specific time input"""
    return await handle_time_input(update, context, parse_specific_time)

async def delay_time_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    """Handle delay time input"""
    return await handle_time_input(update, context, parse_delay_time)

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /cancel command"""
    if 'state' in context.user_data:
        context.user_data.clear()
        await update.message.reply_text(MESSAGES['operation_cancelled'])
    else:
        await update.message.reply_text(MESSAGES['invalid_operation'])

async def list_reminders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /list command"""
    db = DatabaseHandler()
    try:
        reminders = db.get_active_reminders(update.effective_user.id)
        if not reminders:
            await update.message.reply_text(MESSAGES['no_active_reminders'])
            return
        
        response = "Ваші активні нагадування:\n\n"
        for reminder in reminders:
            formatted_time = format_reminder_time(reminder.reminder_time)
            response += f"🔔 {formatted_time}\n{reminder.text}\n\n"
        
        await update.message.reply_text(response)
    finally:
        db.close()

async def save_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                       reminder_time: datetime) -> None:
    """Save reminder to database and schedule it"""
    db = DatabaseHandler()
    try:
        reminder = db.add_reminder(
            user_id=update.effective_user.id,
            text=context.user_data['reminder_text'],
            reminder_time=reminder_time
        )
        
        context.job_queue.run_once(
            send_reminder,
            when=reminder_time,
            data={'chat_id': update.effective_chat.id, 'reminder_id': reminder.id}
        )
        
        await update.message.reply_text(
            MESSAGES['reminder_set'].format(format_reminder_time(reminder_time))
        )
    finally:
        db.close()
        context.user_data.clear()

async def send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send reminder message when time comes"""
    job = context.job
    chat_id = job.data['chat_id']
    reminder_id = job.data['reminder_id']
    
    db = DatabaseHandler()
    try:
        reminder = db.get_reminder(reminder_id)
        if reminder and reminder.is_active:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🔔 Нагадування!\n\n{reminder.text}"
            )
            db.deactivate_reminder(reminder_id)
    finally:
        db.close()

def get_state_handler(state: str) -> callable:
    """Return appropriate handler based on state"""
    handlers = {
        States.WAITING_FOR_TEXT: handle_reminder_text,
        States.ENTERING_SPECIFIC_TIME: specific_time_handler,
        States.ENTERING_DELAY_TIME: delay_time_handler
    }
    return handlers.get(state)