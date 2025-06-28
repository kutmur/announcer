"""
Main entry point for BTU Announcer Bot (Production Version)
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

from handlers.commands_production import (
    start_command, 
    help_command, 
    update_command, 
    handle_department_selection,
    error_handler,
    send_announcement_to_user,
    format_announcement_message
)
from handlers.scraper import AnnouncementScraper
from handlers.database import DatabaseHandler
from handlers.departments import get_department_names, get_department_url

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BTUAnnouncerBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        
        # Create single instances of components
        self.scraper = AnnouncementScraper()
        self.db = DatabaseHandler()
        
        # Store instances in bot_data for access by handlers
        self.application.bot_data['scraper'] = self.scraper
        self.application.bot_data['db'] = self.db
        
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup command and message handlers"""
        try:
            # Command handlers
            self.application.add_handler(CommandHandler("start", start_command))
            self.application.add_handler(CommandHandler("help", help_command))
            self.application.add_handler(CommandHandler("update", update_command))
            
            # Message handler for department selection
            self.application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_department_selection)
            )
            
            # Error handler
            self.application.add_error_handler(error_handler)
            
            logger.info("All handlers setup successfully")
        except Exception as e:
            logger.error(f"Error setting up handlers: {e}")
            raise
    
    async def check_all_departments(self):
        """Check all departments for new announcements and notify users"""
        logger.info("Starting scheduled announcement check for all departments")
        
        departments = get_department_names()
        total_notifications = 0
        
        for department in departments:
            try:
                # Get users subscribed to this department
                users = self.db.get_users_by_department(department)
                if not users:
                    continue  # Skip if no users subscribed
                
                logger.info(f"Checking {department} for {len(users)} users")
                
                # Get department URL and scrape
                url = get_department_url(department)
                if not url:
                    logger.warning(f"No URL found for department: {department}")
                    continue
                
                announcements = self.scraper.scrape_announcements(url, max_announcements=5)
                
                if not announcements:
                    logger.info(f"No announcements found for {department}")
                    continue
                
                # Check for new announcements
                new_announcements = []
                for announcement in announcements:
                    if not self.db.is_announcement_sent(department, announcement['hash']):
                        new_announcements.append(announcement)
                
                if new_announcements:
                    logger.info(f"Found {len(new_announcements)} new announcements for {department}")
                    
                    # Send to all subscribed users
                    for user in users:
                        for announcement in new_announcements:
                            try:
                                success = await send_announcement_to_user(
                                    user['user_id'], 
                                    announcement, 
                                    department,
                                    self.application.bot
                                )
                                if success:
                                    total_notifications += 1
                            except Exception as e:
                                logger.error(f"Error sending to user {user['user_id']}: {e}")
                    
                    # Mark announcements as sent
                    for announcement in new_announcements:
                        self.db.mark_announcement_sent(
                            department, 
                            announcement['hash'], 
                            announcement['title']
                        )
                
                # Small delay between departments to avoid overwhelming the server
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error checking department {department}: {e}")
                continue
        
        logger.info(f"Finished scheduled check. Sent {total_notifications} notifications")
        return total_notifications
    
    async def scheduled_check_job(self):
        """Background job for scheduled announcement checking"""
        while True:
            try:
                current_time = datetime.now()
                logger.info(f"Running scheduled check at {current_time}")
                
                await self.check_all_departments()
                
                # Clean up old announcements once a day
                if current_time.hour == 2:  # 2 AM cleanup
                    self.db.cleanup_old_announcements(days_to_keep=30)
                
                # Wait 30 minutes before next check
                await asyncio.sleep(30 * 60)  # 30 minutes
                
            except Exception as e:
                logger.error(f"Error in scheduled job: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def start_bot(self):
        """Start the bot with both polling and scheduled tasks"""
        logger.info("Starting BTU Announcer Bot...")
        
        # Start the bot
        await self.application.initialize()
        await self.application.start()
        
        # Log bot info
        try:
            bot_info = await self.application.bot.get_me()
            logger.info(f"Bot initialized successfully: {bot_info.first_name} (@{bot_info.username})")
        except Exception as e:
            logger.error(f"Failed to get bot info: {e}")
        
        # Start polling in the background
        polling_task = asyncio.create_task(self.application.updater.start_polling())
        
        # Start scheduled checking
        scheduled_task = asyncio.create_task(self.scheduled_check_job())
        
        logger.info("Bot started successfully! Polling for messages and checking announcements...")
        
        try:
            # Wait for both tasks
            await asyncio.gather(polling_task, scheduled_task)
        except KeyboardInterrupt:
            logger.info("Shutting down bot...")
        finally:
            await self.application.stop()
            await self.application.shutdown()
    
    def run(self):
        """Run the bot"""
        asyncio.run(self.start_bot())


async def main():
    """Main function"""
    # Get bot token from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        logger.error("Please set your bot token in the .env file")
        return
    
    # Create and run bot
    bot = BTUAnnouncerBot(token)
    await bot.start_bot()


if __name__ == "__main__":
    # If running directly, use the simpler approach
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found!")
        print("Please add your bot token to the .env file:")
        print("TELEGRAM_BOT_TOKEN=your_bot_token_here")
        exit(1)
    
    print("🤖 Starting BTU Announcer Bot...")
    print("📝 Bot will check for announcements every 30 minutes")
    print("🛑 Press Ctrl+C to stop")
    
    bot = BTUAnnouncerBot(token)
    
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped!")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        logger.error(f"Fatal error: {e}")
