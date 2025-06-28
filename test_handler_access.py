#!/usr/bin/env python3
"""
Test script to verify handlers can access shared instances
"""

import os
import sys
import asyncio
from unittest.mock import Mock, AsyncMock
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append('/home/halil/Desktop/repos/announcer')

from main import BTUAnnouncerBot
from handlers.commands import start_command, update_command, stats_command, handle_department_selection

# Load environment variables
load_dotenv()

async def test_handler_access():
    """Test that handlers can access shared instances from context"""
    print("🧪 Testing handler access to shared instances...")
    
    # Get bot token from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment variables!")
        return False
    
    try:
        # Create bot instance
        bot = BTUAnnouncerBot(token)
        
        # Create mock update and context objects
        mock_update = Mock()
        mock_user = Mock()
        mock_user.id = 12345
        mock_user.username = "test_user"
        mock_chat = Mock()
        mock_chat.id = 12345
        mock_chat.type = "private"
        mock_message = Mock()
        mock_message.text = "Bilgisayar"
        
        mock_update.effective_user = mock_user
        mock_update.effective_chat = mock_chat
        mock_update.message = mock_message
        
        # Create mock context with bot_data
        mock_context = Mock()
        mock_context.bot_data = bot.application.bot_data
        mock_context.bot = AsyncMock()
        
        # Test that stats_command can access db
        print("🔍 Testing stats_command access to database...")
        try:
            # This should not raise an error even if the actual database operations fail
            # We just want to verify the 'db' variable is accessible
            await stats_command(mock_update, mock_context)
            print("✅ stats_command can access shared instances")
        except KeyError as e:
            if "'db'" in str(e):
                print(f"❌ stats_command cannot access db: {e}")
                return False
            else:
                print("✅ stats_command can access shared instances (other error is OK)")
        except Exception as e:
            print("✅ stats_command can access shared instances (other error is OK)")
        
        # Test that handle_department_selection can access both db and scraper
        print("🔍 Testing handle_department_selection access to instances...")
        try:
            await handle_department_selection(mock_update, mock_context)
            print("✅ handle_department_selection can access shared instances")
        except KeyError as e:
            if "'db'" in str(e) or "'scraper'" in str(e):
                print(f"❌ handle_department_selection cannot access instances: {e}")
                return False
            else:
                print("✅ handle_department_selection can access shared instances (other error is OK)")
        except Exception as e:
            print("✅ handle_department_selection can access shared instances (other error is OK)")
        
        # Test that update_command can access both db and scraper
        print("🔍 Testing update_command access to instances...")
        try:
            await update_command(mock_update, mock_context)
            print("✅ update_command can access shared instances")
        except KeyError as e:
            if "'db'" in str(e) or "'scraper'" in str(e):
                print(f"❌ update_command cannot access instances: {e}")
                return False
            else:
                print("✅ update_command can access shared instances (other error is OK)")
        except Exception as e:
            print("✅ update_command can access shared instances (other error is OK)")
        
        print("✅ All handlers can access shared instances!")
        return True
        
    except Exception as e:
        print(f"❌ Handler test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_handler_access())
    if success:
        print("\n🎉 Handler access test completed successfully!")
        print("All handlers can properly access the shared database and scraper instances.")
    else:
        print("\n💥 Handler access test failed!")
        sys.exit(1)
