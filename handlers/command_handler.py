# command_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from typing import Optional
from database.db_handler import DatabaseHandler
from utils.keyboard_maker import get_time_choice_keyboard
from utils.time_parser import format_reminder_time, parse_specific_time, parse_delay_time
from datetime import datetime
from config import Config

class ConversationStates:
    """States for conversation handling"""
    WAITING_FOR_TEXT = 'waiting_for_reminder_text'
    CHOOSING_TIME_TYPE = 'choosing_time_type'
    ENTERING_SPECIFIC_TIME = 'entering_specific_time'
    ENTERING_DELAY_TIME = 'entering_delay_time'
    ENTERING_SNOOZE_TIME = 'entering_snooze_time'

class CommandHandler:
    """Unified handler for all bot commands and message processing"""
    
    def __init__(self):
        self.db = DatabaseHandler()
        self.messages = Config.MESSAGES

    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        await update.message.reply_text(self.messages['welcome'])

    async def help_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        await update.message.reply_text(self.messages['help'])

    async def new_reminder_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Handle /new command and start reminder creation process"""
        context.user_data['state'] = ConversationStates.WAITING_FOR_TEXT
        await update.message.reply_text(self.messages['reminder_text'])
        return ConversationStates.WAITING_FOR_TEXT

    async def handle_reminder_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Process reminder text input"""
        context.user_data['reminder_text'] = update.message.text
        context.user_data['state'] = ConversationStates.CHOOSING_TIME_TYPE
        await update.message.reply_text(
            self.messages['choose_time'],
            reply_markup=get_time_choice_keyboard()
        )
        return ConversationStates.CHOOSING_TIME_TYPE

    async def handle_time_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                              parse_func: callable) -> Optional[str]:
        """Generic handler for both specific and delay time inputs"""
        try:
            reminder_time = parse_func(update.message.text)
            await self._save_reminder(update, context, reminder_time)
            return None
        except ValueError:
            await update.message.reply_text(self.messages['invalid_time'])
            return context.user_data['state']

    async def specific_time_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
        """Handle specific time input"""
        return await self.handle_time_input(update, context, parse_specific_time)

    async def delay_time_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
        """Handle delay time input"""
        return await self.handle_time_input(update, context, parse_delay_time)

    async def list_reminders_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /list command"""
        try:
            reminders = self.db.get_active_reminders(update.effective_user.id)
            if not reminders:
                await update.message.reply_text(self.messages['no_active_reminders'])
                return

            response = "Ваші активні нагадування:\n\n"
            for reminder in reminders:
                formatted_time = format_reminder_time(reminder.reminder_time)
                response += f"🔔 {formatted_time}\n{reminder.text}\n\n"

            await update.message.reply_text(response)
        except Exception as e:
            await update.message.reply_text(f"Помилка при отриманні списку нагадувань: {str(e)}")

    async def cancel_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /cancel command"""
        if 'state' in context.user_data:
            context.user_data.clear()
            await update.message.reply_text(self.messages['operation_cancelled'])
        else:
            await update.message.reply_text(self.messages['invalid_operation'])

    async def _save_reminder(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                           reminder_time: datetime) -> None:
        """Save reminder to database and schedule it"""
        try:
            reminder = self.db.add_reminder(
                user_id=update.effective_user.id,
                text=context.user_data['reminder_text'],
                reminder_time=reminder_time
            )

            context.job_queue.run_once(
                self._send_reminder,
                when=reminder_time,
                data={'chat_id': update.effective_chat.id, 'reminder_id': reminder.id}
            )

            await update.message.reply_text(
                self.messages['reminder_set'].format(format_reminder_time(reminder_time))
            )
        finally:
            context.user_data.clear()

    async def _send_reminder(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send reminder message when time comes"""
        job = context.job
        chat_id = job.data['chat_id']
        reminder_id = job.data['reminder_id']

        try:
            reminder = self.db.get_reminder(reminder_id)
            if reminder and reminder.is_active:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🔔 Нагадування!\n\n{reminder.text}"
                )
                self.db.deactivate_reminder(reminder_id)
        except Exception as e:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Помилка при відправці нагадування: {str(e)}"
            )

    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, 'db'):
            self.db.close()