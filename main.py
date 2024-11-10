# main.py
import logging
from telegram.ext import (
    Application,
    CommandHandler as TelegramCommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    
)

from telegram import Update

from config import Config
from handlers.command_handler import CommandHandler, ConversationStates
from handlers.callback_handler import CallbackHandlers

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ReminderBot:
    """Main bot class that handles all setup and initialization"""
    
    def __init__(self):
        """Initialize bot with handlers"""
        self.application = Application.builder().token(Config.BOT_TOKEN).build()
        self.command_handler = CommandHandler()
        self.callback_handlers = CallbackHandlers()
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Setup all bot handlers"""
        # Add conversation handler
        self.application.add_handler(self._create_conversation_handler())
        
        # Add basic command handlers
        self.application.add_handler(
            TelegramCommandHandler('start', self.command_handler.start_handler)
        )
        self.application.add_handler(
            TelegramCommandHandler('help', self.command_handler.help_handler)
        )
        self.application.add_handler(
            TelegramCommandHandler('list', self.command_handler.list_reminders_handler)
        )
        
        # Add callback query handler
        self.application.add_handler(
            CallbackQueryHandler(self.callback_handlers.handle_callback)
        )

        # Add error handler
        self.application.add_error_handler(self._error_handler)

    def _create_conversation_handler(self) -> ConversationHandler:
        """Create and return the conversation handler"""
        return ConversationHandler(
            entry_points=[
                TelegramCommandHandler('new', self.command_handler.new_reminder_handler)
            ],
            states={
                ConversationStates.WAITING_FOR_TEXT: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        self.command_handler.handle_reminder_text
                    )
                ],
                ConversationStates.CHOOSING_TIME_TYPE: [
                    CallbackQueryHandler(
                        self.callback_handlers.handle_time_type,
                        pattern='^time_type:'
                    )
                ],
                ConversationStates.ENTERING_SPECIFIC_TIME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        self.command_handler.specific_time_handler
                    )
                ],
                ConversationStates.ENTERING_DELAY_TIME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        self.command_handler.delay_time_handler
                    )
                ]
            },
            fallbacks=[
                TelegramCommandHandler('cancel', self.command_handler.cancel_handler)
            ]
        )

    async def _error_handler(self, update: object, context: object) -> None:
        """Log errors and send a message to the user"""
        logger.error(f"Exception while handling an update: {context.error}")
        
        if update and hasattr(update, 'effective_chat'):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Вибачте, сталася помилка при обробці вашого запиту."
            )

    async def setup_commands(self) -> None:
        """Setup bot commands in Telegram interface"""
        await self.application.bot.set_my_commands([
            (command, description) 
            for command, description in Config.COMMANDS.items()
        ])

    def run(self) -> None:
        """Start the bot"""
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

def main() -> None:
    """Main function to run the bot"""
    bot = ReminderBot()
    bot.run()

if __name__ == '__main__':
    main()