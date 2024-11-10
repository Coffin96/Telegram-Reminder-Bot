from telegram import Update
from telegram.ext import ContextTypes
from config import Config
from database.db_handler import DatabaseHandler
from utils.keyboard_maker import get_reminder_management_keyboard
from typing import Optional, Callable, Dict
from dataclasses import dataclass

@dataclass
class CallbackTypes:
    """Constants for callback types"""
    TIME_TYPE: str = 'time_type'
    DELETE_REMINDER: str = 'delete_reminder'
    SNOOZE_REMINDER: str = 'snooze_reminder'

class CallbackHandlers:
    """Handler class for callback queries"""

    def __init__(self):
        """Initialize callback handlers mapping"""
        self._handlers: Dict[str, Callable] = {
            CallbackTypes.TIME_TYPE: self.handle_time_type,
            CallbackTypes.DELETE_REMINDER: self.handle_delete_reminder,
            CallbackTypes.SNOOZE_REMINDER: self.handle_snooze_reminder
        }

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Main callback query handler"""
        query = update.callback_query
        await query.answer()

        if not query.data:
            return

        callback_type, *params = query.data.split(':')
        handler = self._handlers.get(callback_type)
        
        if handler:
            await handler(update, context, params[0] if params else None)

    async def handle_time_type(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        time_type: Optional[str]
    ) -> None:
        """Handle time type selection"""
        query = update.callback_query
        
        if time_type == 'specific':
            context.user_data['state'] = 'waiting_for_specific_time'
            await query.message.edit_text(Config.MESSAGES['enter_specific_time'])
        
        elif time_type == 'delay':
            context.user_data['state'] = 'waiting_for_delay_time'
            await query.message.edit_text(Config.MESSAGES['enter_delay_time'])

    async def handle_delete_reminder(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        reminder_id: Optional[str]
    ) -> None:
        """Handle reminder deletion"""
        if not reminder_id:
            return
            
        query = update.callback_query
        async with DatabaseHandler() as db:
            if await db.delete_reminder(int(reminder_id), query.from_user.id):
                await query.message.edit_text(Config.MESSAGES['reminder_deleted'])
            else:
                await query.message.edit_text(Config.MESSAGES['reminder_not_found'])

    async def handle_snooze_reminder(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        reminder_id: Optional[str]
    ) -> None:
        """Handle reminder snooze request"""
        if not reminder_id:
            return
            
        query = update.callback_query
        context.user_data['snooze_reminder_id'] = int(reminder_id)
        context.user_data['state'] = 'waiting_for_snooze_time'
        await query.message.edit_text(Config.MESSAGES['enter_snooze_time'])

    async def handle_reminder_response(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        reminder_id: int
    ) -> None:
        """Handle user response to a reminder"""
        keyboard = get_reminder_management_keyboard(reminder_id)
        await update.message.reply_text(
            Config.MESSAGES['reminder_management'],
            reply_markup=keyboard
        )