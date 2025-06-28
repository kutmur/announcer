"""
Telegram bot command handlers for BTU Announcer Bot
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
    
    # Test data - sample department list for debugging keyboard issues
    test_departments = ["Bilgisayar", "Yapay Zeka", "Makine", "Elektrik", "İnşaat"]
    
    # Try to get department list from the actual function
    try:
        departments = get_department_names()
        if not departments:
            logger.warning("get_department_names() returned empty list, using test data")
            departments = test_departments
        else:
            logger.info(f"Successfully loaded {len(departments)} departments from get_department_names()")
    except Exception as e:
        logger.error(f"Error calling get_department_names(): {e}, using test data")
        departments = test_departments
    
    logger.info(f"Using {len(departments)} departments for keyboard: {departments[:3]}...")
    
    # Create keyboard with department options - 2 departments per row
    keyboard = []
    
    # Sort departments alphabetically for better organization
    sorted_departments = sorted(departments)
    
    # Group departments 2 per row
    for i in range(0, len(sorted_departments), 2):
        if i + 1 < len(sorted_departments):
            # Two departments in this row
            keyboard.append([sorted_departments[i], sorted_departments[i + 1]])
        else:
            # Only one department left (odd number)
            keyboard.append([sorted_departments[i]])
    
    # Add special buttons at the end
    keyboard.append(["📊 İstatistikler", "❓ Yardım"])
    keyboard.append(["⌨️ Klavyeyi Gizle"])
    
    logger.info(f"Created keyboard with {len(keyboard)} rows (2 departments per row)")
    logger.info(f"Keyboard structure: {keyboard}")
    
    # Create reply markup
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True, 
        one_time_keyboard=False
    )
    
    # 1. Send the welcome message without keyboard
    welcome_message = "🎓 BTÜ Duyuru Botu'na Hoş Geldiniz!\n\n📋 Nasıl Kullanılır:\n1. Menüden bölüm seçin\n2. Bot duyuruları takip etsin\n3. Yeni duyurular bildirilsin"
    
    try:
        await context.bot.send_message(
            chat_id=chat.id,
            text=welcome_message,
            parse_mode="Markdown"
        )
        logger.info(f"✅ Sent welcome message to user {user.id}")
    except Exception as e:
        logger.error(f"❌ Failed to send welcome message: {e}")
        return
    
    # 2. Send the keyboard with a short message
    try:
        keyboard_message = "👇 Lütfen bölümünüzü seçin:"
        await context.bot.send_message(
            chat_id=chat.id,
            text=keyboard_message,
            reply_markup=reply_markup
        )
        logger.info(f"✅ Sent keyboard to user {user.id} with {len(keyboard)} rows")
        logger.info(f"✅ Keyboard buttons confirmed: {[row for row in keyboard]}")
    except Exception as e:
        logger.error(f"❌ Failed to send keyboard: {e}")
        await context.bot.send_message(
            chat_id=chat.id,
            text="❌ Klavye gösterilemedi. Lütfen tekrar /start komutunu deneyin."
        )


async def hide_keyboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /hide command - remove the keyboard"""
    user = update.effective_user
    logger.info(f"User {user.username} ({user.id}) requested to hide keyboard")
    
    reply_markup = ReplyKeyboardRemove()
    
    await update.message.reply_text(
        "⌨️ Klavye kaldırıldı. Tekrar görmek için `/start` komutunu kullanın.",
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = """
🤖 **BTÜ Duyuru Botu Yardım**

**Mevcut Komutlar:**
• `/start` - Botu başlat ve bölüm seçim menüsünü göster
• `/update` - Manuel duyuru kontrolü yap
• `/help` - Bu yardım mesajını göster
• `/stats` - Bot istatistiklerini göster
• `/hide` - Bölüm seçim menüsünü gizle

**🔧 Debug Komutları:**
• `/test` - Klavye testi yap
• `/status` - Bot durumunu kontrol et
• `/permissions` - Bot izinlerini kontrol et

**📱 Bölüm Seçimi:**
1. `/start` komutunu kullanın
2. Açılan menüden bölümünüzü seçin
3. Menüdeki butonlara tıklayarak seçim yapın
4. Manuel yazım yapmayın - sadece butonları kullanın

**Nasıl Çalışır:**
1. Bölümünüzü seçtikten sonra bot o bölümün duyuru sayfasını düzenli olarak kontrol eder
2. Yeni duyurular bulunduğunda size otomatik bildirim gönderir
3. Sadece daha önce gönderilmemiş duyurular bildirilir

**Desteklenen Bölümler:**
Bot BTÜ'nün tüm fakültelerinden 30 bölümü destekler.

**❓ Sorun mu var?**
• Menü görünmüyorsa `/start` komutunu tekrar kullanın
• Klavye testi için `/test` komutunu kullanın
• Bot durumu için `/status` komutunu kullanın
• Yanlış bölüm seçtiyseniz `/start` ile yeniden başlayın
• Bot düzgün çalışmıyorsa `/start` komutu ile yeniden başlatabilirsiniz
    """
    
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


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stats command - show bot statistics"""
    try:
        # Get shared instances from context
        db = context.bot_data['db']
        
        stats = db.get_stats()
        user_data = db.get_user_subscription(update.effective_user.id)
        
        stats_text = f"""
📊 **Bot İstatistikleri**

👥 **Kullanıcılar:**
• Toplam kullanıcı: {stats['total_users']}
• Aktif kullanıcı: {stats['active_users']}

📢 **Duyurular:**
• Toplam gönderilen: {stats['total_sent_announcements']}

👤 **Sizin Durumunuz:**"""
        
        if user_data:
            user_dept_count = db.get_sent_announcements_count(user_data['department'])
            stats_text += f"""
• Bölümünüz: {user_data['department']}
• Bu bölümden gönderilen: {user_dept_count} duyuru"""
        else:
            stats_text += "\n• Henüz bir bölüm seçmemişsiniz"
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"Error showing stats: {e}")
        await update.message.reply_text("❌ İstatistikler yüklenirken hata oluştu.")


async def handle_department_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle department selection from keyboard"""
    user = update.effective_user
    selected_text = update.message.text
    
    logger.info(f"User {user.username} ({user.id}) selected: '{selected_text}'")
    
    # Get shared instances from context
    db = context.bot_data['db']
    scraper = context.bot_data['scraper']
    
    # Handle special buttons
    if selected_text == '📊 İstatistikler':
        await stats_command(update, context)
        return
    elif selected_text == '❓ Yardım':
        await help_command(update, context)
        return
    elif selected_text == '⌨️ Klavyeyi Gizle':
        await hide_keyboard_command(update, context)
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


async def test_keyboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test command to verify keyboard functionality"""
    user = update.effective_user
    chat = update.effective_chat
    
    logger.info(f"Testing keyboard for user {user.id} in chat {chat.id}")
    
    # Simple test keyboard
    test_keyboard = [
        ['Test Button 1', 'Test Button 2'],
        ['Test Button 3']
    ]
    
    reply_markup = ReplyKeyboardMarkup(
        test_keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        selective=False
    )
    
    try:
        await context.bot.send_message(
            chat_id=chat.id,
            text="🧪 **Keyboard Test**\n\nBu bir test mesajıdır. Aşağıdaki butonları görebiliyor musunuz?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        logger.info(f"✅ Test keyboard sent successfully to user {user.id}")
    except Exception as e:
        logger.error(f"❌ Test keyboard failed: {e}")
        await context.bot.send_message(
            chat_id=chat.id,
            text=f"❌ Test keyboard failed: {e}"
        )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check bot status and connection"""
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        # Test bot connection
        bot_info = await context.bot.get_me()
        
        status_message = f"""🤖 **Bot Durumu**

✅ **Bot Bilgileri:**
• İsim: {bot_info.first_name}
• Kullanıcı Adı: @{bot_info.username}
• ID: {bot_info.id}

👤 **Kullanıcı Bilgileri:**
• ID: {user.id}
• Kullanıcı Adı: {user.username or 'Yok'}
• Chat ID: {chat.id}
• Chat Tipi: {chat.type}

🔧 **Bağlantı Durumu:** ✅ Aktif

📝 **Test Mesajı:** Bu mesaj başarıyla gönderildi."""
        
        await context.bot.send_message(
            chat_id=chat.id,
            text=status_message,
            parse_mode='Markdown'
        )
        
        logger.info(f"Status command executed successfully for user {user.id}")
        
    except Exception as e:
        logger.error(f"Status command failed: {e}")
        await context.bot.send_message(
            chat_id=chat.id,
            text=f"❌ Bot durumu kontrol edilemedi: {e}"
        )


async def permissions_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check bot permissions"""
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        # Get chat member info
        chat_member = await context.bot.get_chat_member(chat.id, context.bot.id)
        
        permissions_message = f"""🔐 **Bot İzinleri**

👤 **Kullanıcı:** {user.username or 'Yok'} ({user.id})
💬 **Chat:** {chat.title or 'Private'} ({chat.id})
📝 **Chat Tipi:** {chat.type}

🤖 **Bot İzinleri:**
• Can Send Messages: {chat_member.can_send_messages or 'N/A'}
• Can Send Media Messages: {chat_member.can_send_media_messages or 'N/A'}
• Can Send Other Messages: {chat_member.can_send_other_messages or 'N/A'}
• Can Add Web Page Previews: {chat_member.can_add_web_page_previews or 'N/A'}

🔧 **Bot Durumu:** {chat_member.status}"""
        
        await context.bot.send_message(
            chat_id=chat.id,
            text=permissions_message,
            parse_mode='Markdown'
        )
        
        logger.info(f"Permissions checked for user {user.id}")
        
    except Exception as e:
        logger.error(f"Permissions check failed: {e}")
        await context.bot.send_message(
            chat_id=chat.id,
            text=f"❌ İzinler kontrol edilemedi: {e}"
        )
