"""
Standalone /start command handler for testing keyboard functionality
This is a complete, testable implementation that uses sample data to debug keyboard issues.
"""

import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start_command_test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Complete, testable /start command handler with sample data
    This uses manually defined departments to test keyboard functionality
    """
    user = update.effective_user
    chat = update.effective_chat
    
    # Validate that this is a private chat
    if chat.type != "private":
        logger.warning(f"Start command called in non-private chat: {chat.type}")
        return
    
    # Validate user and chat
    if not user or not chat:
        logger.error("Invalid user or chat in start command")
        return
    
    logger.info(f"🚀 User {user.username} ({user.id}) started the bot in chat {chat.id}")
    
    # Sample department list for testing (exactly as requested)
    departments = ["Bilgisayar", "Yapay Zeka", "Makine", "Elektrik", "İnşaat"]
    
    logger.info(f"📋 Using {len(departments)} test departments: {departments}")
    
    # Build keyboard 2 per row (exactly as requested)
    keyboard = []
    for i in range(0, len(departments), 2):
        if i + 1 < len(departments):
            # Two departments in this row
            keyboard.append([departments[i], departments[i + 1]])
        else:
            # Only one department left (odd number)
            keyboard.append([departments[i]])
    
    logger.info(f"⌨️ Created keyboard with {len(keyboard)} department rows")
    
    # Create reply markup
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True, 
        one_time_keyboard=False
    )
    
    try:
        # 1. Send welcome message
        welcome_text = "🎓 BTÜ Duyuru Botu'na Hoş Geldiniz!\n\n📋 Nasıl Kullanılır:\n1. Menüden bölüm seçin\n2. Bot duyuruları takip etsin\n3. Yeni duyurular bildirilsin"
        
        await context.bot.send_message(
            chat_id=chat.id,
            text=welcome_text,
            parse_mode="Markdown"
        )
        logger.info(f"✅ Sent welcome message to user {user.id}")
        
        # 2. Send keyboard message
        keyboard_text = "👇 Lütfen bölümünüzü seçin:"
        
        await context.bot.send_message(
            chat_id=chat.id,
            text=keyboard_text,
            reply_markup=reply_markup
        )
        logger.info(f"✅ Sent keyboard to user {user.id}")
        logger.info(f"✅ Keyboard structure: {keyboard}")
        
        # Log confirmation that buttons should be showing
        logger.info(f"🎯 KEYBOARD CONFIRMATION:")
        logger.info(f"   - Total rows: {len(keyboard)}")
        logger.info(f"   - Departments: {departments}")
        logger.info(f"   - resize_keyboard: True")
        logger.info(f"   - one_time_keyboard: False")
        logger.info(f"   - ReplyKeyboardMarkup should be visible!")
        
    except Exception as e:
        logger.error(f"❌ Error in start_command_test: {e}")
        await context.bot.send_message(
            chat_id=chat.id,
            text="❌ Bir hata oluştu. Lütfen tekrar deneyin."
        )


# Alternative implementation with try-catch for department loading
async def start_command_robust(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Robust /start command that falls back to test data if real data fails
    """
    user = update.effective_user
    chat = update.effective_chat
    
    if not user or not chat or chat.type != "private":
        return
    
    logger.info(f"🚀 Robust start command for user {user.id}")
    
    # Test departments as fallback
    test_departments = ["Bilgisayar", "Yapay Zeka", "Makine", "Elektrik", "İnşaat"]
    
    # Try to load real departments
    try:
        from handlers.departments import get_department_names
        departments = get_department_names()
        
        if not departments:
            logger.warning("⚠️ get_department_names() returned empty, using test data")
            departments = test_departments
        else:
            logger.info(f"✅ Loaded {len(departments)} real departments")
            
    except ImportError as e:
        logger.error(f"❌ Import error: {e}, using test data")
        departments = test_departments
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}, using test data")
        departments = test_departments
    
    # Build keyboard 2 per row
    keyboard = []
    for i in range(0, len(departments), 2):
        if i + 1 < len(departments):
            keyboard.append([departments[i], departments[i + 1]])
        else:
            keyboard.append([departments[i]])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    try:
        # Send both messages
        await context.bot.send_message(chat_id=chat.id, text="🎓 BTÜ Duyuru Botu'na Hoş Geldiniz!\n\n📋 Nasıl Kullanılır:\n1. Menüden bölüm seçin\n2. Bot duyuruları takip etsin\n3. Yeni duyurular bildirilsin", parse_mode="Markdown")
        
        await context.bot.send_message(chat_id=chat.id, text="👇 Lütfen bölümünüzü seçin:", reply_markup=reply_markup)
        
        logger.info(f"✅ Successfully sent messages with keyboard to user {user.id}")
        logger.info(f"🎯 Keyboard: {keyboard}")
        
    except Exception as e:
        logger.error(f"❌ Failed to send messages: {e}")


if __name__ == "__main__":
    print("🧪 This file contains test /start command handlers")
    print("Use start_command_test() or start_command_robust() in your bot")
    print("\nKeyboard structure test:")
    
    departments = ["Bilgisayar", "Yapay Zeka", "Makine", "Elektrik", "İnşaat"]
    keyboard = []
    for i in range(0, len(departments), 2):
        if i + 1 < len(departments):
            keyboard.append([departments[i], departments[i + 1]])
        else:
            keyboard.append([departments[i]])
    
    print(f"Departments: {departments}")
    print(f"Keyboard: {keyboard}")
