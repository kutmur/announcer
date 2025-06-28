"""
Telegram bot command handlers for BTU Announcer Bot (Production Version)
"""

import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from handlers.departments import get_department_names, get_department_url

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - show department selection menu"""
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
    
    logger.info(f"User {user.username} ({user.id}) started the bot in chat {chat.id} ({chat.type})")
    
    # Get department list
    departments = get_department_names()
    logger.info(f"Successfully loaded {len(departments)} departments")
    
    # Create keyboard with department options - 1 department per row for better mobile UX
    keyboard = []
    
    # Sort departments alphabetically for better organization
    sorted_departments = sorted(departments)
    
    # Add each department as a separate row (1 per row)
    for department in sorted_departments:
        keyboard.append([department])
    
    # Add help button at the end as a single row
    keyboard.append(["❓ Yardım"])
    
    logger.info(f"Created keyboard with {len(keyboard)} rows (1 department per row)")
    
    # Create reply markup
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True, 
        one_time_keyboard=False
    )
    
    # Send combined welcome message with keyboard
    welcome_message = """🎓 **BTÜ Duyuru Botu'na Hoş Geldiniz!**

📋 **Nasıl Kullanılır:**
1. Aşağıdaki menüden bölümünüzü seçin
2. Bot duyuruları otomatik takip etsin
3. Yeni duyurular size bildirilsin

👇 **Lütfen bölümünüzü seçin:**"""
    
    try:
        await context.bot.send_message(
            chat_id=chat.id,
            text=welcome_message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        logger.info(f"✅ Sent welcome message with keyboard to user {user.id}")
    except Exception as e:
        logger.error(f"❌ Failed to send welcome message: {e}")
        await context.bot.send_message(
            chat_id=chat.id,
            text="❌ Menü gösterilemedi. Lütfen tekrar /start komutunu deneyin."
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = """🤖 **BTÜ Duyuru Botu Yardım**

**Mevcut Komutlar:**
• `/start` - Botu başlat ve bölüm seçim menüsünü göster
• `/help` - Bu yardım mesajını göster
• `/update` - Manuel duyuru kontrolü yap

**📱 Nasıl Kullanılır:**
1. `/start` komutunu kullanın
2. Açılan menüden bölümünüzü seçin
3. Menüdeki butonlara tıklayarak seçim yapın
4. Manuel yazım yapmayın - sadece butonları kullanın

**🔔 Nasıl Çalışır:**
1. Bölümünüzü seçtikten sonra bot o bölümün duyuru sayfasını düzenli olarak kontrol eder
2. Yeni duyurular bulunduğunda size otomatik bildirim gönderir
3. Sadece daha önce gönderilmemiş duyurular bildirilir

**Desteklenen Bölümler:**
Bot BTÜ'nün tüm fakültelerinden 30 bölümü destekler.

**❓ Sorun mu var?**
• Menü görünmüyorsa `/start` komutunu tekrar kullanın
• Yanlış bölüm seçtiyseniz `/start` ile yeniden başlayın
• Bot düzgün çalışmıyorsa `/start` komutu ile yeniden başlatabilirsiniz"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /update command - manually trigger announcement check"""
    user = update.effective_user
    logger.info(f"User {user.username} ({user.id}) requested manual update")
    
    # Get shared instances from context
    db = context.bot_data['db']
    scraper = context.bot_data['scraper']
    
    # Get user's subscription
    user_data = db.get_user_subscription(user.id)
    
    if not user_data:
        await update.message.reply_text(
            "❌ Önce bir bölüm seçmelisiniz! /start komutunu kullanın."
        )
        return
    
    department = user_data['department']
    await update.message.reply_text(f"🔄 {department} bölümü için duyurular kontrol ediliyor...")
    
    try:
        # Get department URL and scrape
        url = get_department_url(department)
        if not url:
            await update.message.reply_text("❌ Bölüm URL'si bulunamadı.")
            return
        
        announcements = scraper.scrape_announcements(url, max_announcements=3)
        
        if not announcements:
            await update.message.reply_text(
                f"❌ {department} bölümünden duyuru alınamadı. Website erişilebilir olmayabilir."
            )
            return
        
        # Check for new announcements
        new_announcements = []
        for announcement in announcements:
            if not db.is_announcement_sent(department, announcement['hash']):
                new_announcements.append(announcement)
        
        if new_announcements:
            await update.message.reply_text(f"✅ {len(new_announcements)} yeni duyuru bulundu!")
            
            for announcement in new_announcements:
                await send_announcement_to_user(user.id, announcement, department, context.bot)
                db.mark_announcement_sent(department, announcement['hash'], announcement['title'])
        else:
            await update.message.reply_text(
                f"ℹ️ {department} bölümünde yeni duyuru yok. Toplam {len(announcements)} duyuru kontrol edildi."
            )
    
    except Exception as e:
        logger.error(f"Error in manual update for user {user.id}: {e}")
        await update.message.reply_text("❌ Duyuru kontrolü sırasında bir hata oluştu.")


async def handle_department_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle department selection from keyboard"""
    user = update.effective_user
    selected_text = update.message.text
    
    logger.info(f"User {user.username} ({user.id}) selected: '{selected_text}'")
    
    # Get shared instances from context
    db = context.bot_data['db']
    scraper = context.bot_data['scraper']
    
    # Handle special buttons
    if selected_text == '❓ Yardım':
        await help_command(update, context)
        return
    
    # Check if it's a valid department
    departments = get_department_names()
    if selected_text in departments:
        # Save user subscription
        db.add_user_subscription(
            user.id, 
            user.username or f"user_{user.id}", 
            selected_text
        )
        
        logger.info(f"User {user.username} ({user.id}) subscribed to {selected_text}")
        
        success_message = f"""✅ **Başarıyla kayıt oldunuz!**

📚 **Seçilen Bölüm:** {selected_text}

🔔 **Bilgilendirme:**
• Artık bu bölümün yeni duyurularını otomatik olarak alacaksınız
• Duyurular genellikle dakikalar içinde bildirilir
• İstediğiniz zaman `/update` komutu ile manuel kontrol yapabilirsiniz

**İlk duyuru kontrolü yapılıyor...**"""
        
        await update.message.reply_text(success_message, parse_mode='Markdown')
        
        # Trigger initial announcement check
        try:
            url = get_department_url(selected_text)
            if url:
                announcements = scraper.scrape_announcements(url, max_announcements=2)
                
                if announcements:
                    await update.message.reply_text(
                        f"✅ Bağlantı başarılı! {selected_text} bölümünden {len(announcements)} duyuru tespit edildi."
                    )
                    
                    # Mark current announcements as sent to avoid spam
                    for announcement in announcements:
                        db.mark_announcement_sent(selected_text, announcement['hash'], announcement['title'])
                else:
                    await update.message.reply_text(
                        "⚠️ Bölüm sayfasına bağlanıldı ancak duyuru bulunamadı. Bu normal olabilir."
                    )
        except Exception as e:
            logger.error(f"Error in initial check for {selected_text}: {e}")
            await update.message.reply_text(
                "⚠️ İlk kontrol sırasında sorun yaşandı, ancak kayıt başarılı. Sonraki kontroller düzgün çalışacak."
            )
    
    else:
        logger.warning(f"Invalid department selection: '{selected_text}' by user {user.id}")
        
        # Provide helpful error message with suggestion to use keyboard
        error_message = f"""❌ **Geçersiz bölüm seçimi!**

Seçtiğiniz: `{selected_text}`

📋 **Lütfen aşağıdaki menüden bir bölüm seçin:**
• Menüdeki butonlara tıklayarak seçim yapın
• Manuel yazım yapmayın
• Eğer menü görünmüyorsa `/start` komutunu tekrar kullanın

🔧 **Yardım için:** `/help` komutunu kullanabilirsiniz."""
        
        await update.message.reply_text(error_message, parse_mode='Markdown')


async def send_announcement_to_user(user_id: int, announcement: dict, department: str, bot) -> bool:
    """Send announcement message to a specific user"""
    try:
        # Format announcement message
        message = format_announcement_message(announcement, department)
        
        await bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode='Markdown',
            disable_web_page_preview=False
        )
        
        return True
    
    except Exception as e:
        logger.error(f"Error sending announcement to user {user_id}: {e}")
        return False


def format_announcement_message(announcement: dict, department: str) -> str:
    """Format announcement data into a nice message"""
    message = f"🔔 **Yeni Duyuru - {department}**\n\n"
    message += f"📢 **{announcement['title']}**\n\n"
    
    if announcement['date']:
        message += f"📅 **Tarih:** {announcement['date']}\n\n"
    
    if announcement['description']:
        message += f"📝 **Özet:** {announcement['description']}\n\n"
    
    if announcement['link']:
        message += f"🔗 **Detaylar:** [Duyuruyu Oku]({announcement['link']})"
    
    return message


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Bir hata oluştu. Lütfen daha sonra tekrar deneyin."
        )
