#!/usr/bin/env python3
"""
Test script to verify the refactoring is working correctly
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append('/home/halil/Desktop/repos/announcer')

from main import BTUAnnouncerBot

# Load environment variables
load_dotenv()

async def test_bot_initialization():
    """Test that the bot initializes correctly with shared instances"""
    print("🧪 Testing BTU Announcer Bot refactoring...")
    
    # Get bot token from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment variables!")
        return False
    
    try:
        # Create bot instance
        bot = BTUAnnouncerBot(token)
        
        # Check that bot_data contains the shared instances
        if 'db' not in bot.application.bot_data:
            print("❌ Database instance not found in bot_data")
            return False
        
        if 'scraper' not in bot.application.bot_data:
            print("❌ Scraper instance not found in bot_data")
            return False
        
        # Check that instances are accessible
        db = bot.application.bot_data['db']
        scraper = bot.application.bot_data['scraper']
        
        print(f"✅ Database instance type: {type(db).__name__}")
        print(f"✅ Scraper instance type: {type(scraper).__name__}")
        
        # Check that the main bot also has references
        print(f"✅ Bot database instance type: {type(bot.db).__name__}")
        print(f"✅ Bot scraper instance type: {type(bot.scraper).__name__}")
        
        # Verify they are the same instances
        if bot.db is db and bot.scraper is scraper:
            print("✅ Instances are properly shared!")
        else:
            print("❌ Instances are not properly shared!")
            return False
        
        print("✅ Bot initialization test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Bot initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_bot_initialization())
    if success:
        print("\n🎉 Refactoring test completed successfully!")
        print("The bot should now have proper keyboard functionality.")
    else:
        print("\n💥 Refactoring test failed!")
        sys.exit(1)
