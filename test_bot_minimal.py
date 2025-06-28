#!/usr/bin/env python3
"""
Minimal working Telegram bot for testing keyboard functionality
This uses the fixed /start command with test data
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler
from dotenv import load_dotenv

# Import the fixed start command
from handlers.commands import start_command

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Run the bot"""
    # Get bot token from environment
    token = os.getenv('BOT_TOKEN')
    if not token:
        logger.error("❌ BOT_TOKEN not found in environment variables!")
        logger.error("   Please add BOT_TOKEN=your_bot_token to your .env file")
        return
    
    logger.info("🚀 Starting BTU Announcer Bot (Keyboard Test Mode)")
    
    # Create the Application
    application = Application.builder().token(token).build()
    
    # Add command handler
    application.add_handler(CommandHandler("start", start_command))
    
    logger.info("✅ Bot handlers added successfully")
    logger.info("🎯 Ready to test /start command with keyboard functionality")
    logger.info("   - Send /start to the bot")
    logger.info("   - You should see:")
    logger.info("     1. Welcome message")
    logger.info("     2. 'Lütfen bölümünüzü seçin:' message with keyboard")
    logger.info("     3. Keyboard with department buttons (2 per row)")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
