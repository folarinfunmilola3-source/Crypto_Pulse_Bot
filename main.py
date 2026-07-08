import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv

from handlers.commands import (
    start_command, help_command, about_command,
    price_command, trending_command, market_command,
    search_command, rugcheck_command
)
from handlers.callbacks import button_handler, handle_text_messages
from config import BOT_TOKEN

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot"""
    try:
        # Check if token exists
        if not BOT_TOKEN:
            logger.error("❌ BOT_TOKEN not found in environment variables!")
            return
        
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("price", price_command))
        application.add_handler(CommandHandler("trending", trending_command))
        application.add_handler(CommandHandler("market", market_command))
        application.add_handler(CommandHandler("search", search_command))
        application.add_handler(CommandHandler("rugcheck", rugcheck_command))
        
        # Add callback handler for inline buttons
        application.add_handler(CallbackQueryHandler(button_handler))
        
        # Add message handler for text input
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))
        
        # Start bot
        logger.info("🤖 Bot started successfully! Waiting for messages...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")

if __name__ == '__main__':
    main()
