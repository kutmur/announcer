"""
Database handler for tracking sent announcements and user subscriptions
"""

import json
import os
from typing import Dict, List, Set
from tinydb import TinyDB, Query
import logging

logger = logging.getLogger(__name__)


class DatabaseHandler:
    def __init__(self, db_path: str = "data/bot_data.json"):
        self.db_path = db_path
        
        # Ensure data directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir:  # Only create directory if path has a directory component
            os.makedirs(db_dir, exist_ok=True)
        
        self.db = TinyDB(db_path)
        self.users_table = self.db.table('users')
        self.sent_announcements_table = self.db.table('sent_announcements')
        
        # Also ensure announcer directory exists for announcement tracking
        os.makedirs("announcer", exist_ok=True)
    
    def add_user_subscription(self, user_id: int, username: str, department: str):
        """Add or update user subscription to a department"""
        User = Query()
        
        # Check if user exists
        existing_user = self.users_table.search(User.user_id == user_id)
        
        user_data = {
            'user_id': user_id,
            'username': username,
            'department': department,
            'active': True
        }
        
        if existing_user:
            # Update existing user
            self.users_table.update(user_data, User.user_id == user_id)
            logger.info(f"Updated user {username} ({user_id}) subscription to {department}")
        else:
            # Add new user
            self.users_table.insert(user_data)
            logger.info(f"Added new user {username} ({user_id}) subscription to {department}")
    
    def get_users_by_department(self, department: str) -> List[Dict]:
        """Get all active users subscribed to a specific department"""
        User = Query()
        users = self.users_table.search(
            (User.department == department) & (User.active == True)
        )
        return users
    
    def get_user_subscription(self, user_id: int) -> Dict:
        """Get user subscription details"""
        User = Query()
        user = self.users_table.search(User.user_id == user_id)
        return user[0] if user else None
    
    def deactivate_user(self, user_id: int):
        """Deactivate a user subscription"""
        User = Query()
        self.users_table.update({'active': False}, User.user_id == user_id)
        logger.info(f"Deactivated user {user_id}")
    
    def is_announcement_sent(self, department: str, announcement_hash: str) -> bool:
        """Check if an announcement has been sent for a department"""
        Announcement = Query()
        sent = self.sent_announcements_table.search(
            (Announcement.department == department) & 
            (Announcement.hash == announcement_hash)
        )
        return len(sent) > 0
    
    def mark_announcement_sent(self, department: str, announcement_hash: str, announcement_title: str):
        """Mark an announcement as sent for a department"""
        if not self.is_announcement_sent(department, announcement_hash):
            self.sent_announcements_table.insert({
                'department': department,
                'hash': announcement_hash,
                'title': announcement_title,
                'sent_at': self._get_current_timestamp()
            })
            logger.info(f"Marked announcement as sent: {announcement_title[:50]}...")
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        return self.users_table.all()
    
    def get_sent_announcements_count(self, department: str = None) -> int:
        """Get count of sent announcements, optionally filtered by department"""
        if department:
            Announcement = Query()
            return len(self.sent_announcements_table.search(Announcement.department == department))
        return len(self.sent_announcements_table.all())
    
    def cleanup_old_announcements(self, days_to_keep: int = 30):
        """Clean up old sent announcements to prevent database growth"""
        import time
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.now() - timedelta(days=days_to_keep)
        cutoff_timestamp = int(cutoff_time.timestamp())
        
        Announcement = Query()
        removed = self.sent_announcements_table.remove(
            Announcement.sent_at < cutoff_timestamp
        )
        
        if removed:
            logger.info(f"Cleaned up {len(removed)} old announcements")
    
    def _get_current_timestamp(self) -> int:
        """Get current timestamp"""
        import time
        return int(time.time())
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        return {
            'total_users': len(self.users_table.all()),
            'active_users': len(self.users_table.search(Query().active == True)),
            'total_sent_announcements': len(self.sent_announcements_table.all())
        }


# Legacy JSON handler for backward compatibility and last_sent tracking
class JSONHandler:
    def __init__(self, file_path: str = "announcer/last_sent.json"):
        self.file_path = file_path
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load data from JSON file"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading JSON data: {e}")
        
        return {}
    
    def _save_data(self):
        """Save data to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving JSON data: {e}")
    
    def is_announcement_sent(self, department: str, announcement_hash: str) -> bool:
        """Check if announcement was already sent"""
        dept_data = self.data.get(department, {})
        return announcement_hash in dept_data.get('sent_hashes', [])
    
    def mark_announcement_sent(self, department: str, announcement_hash: str, title: str):
        """Mark announcement as sent"""
        if department not in self.data:
            self.data[department] = {'sent_hashes': [], 'last_titles': []}
        
        dept_data = self.data[department]
        
        if announcement_hash not in dept_data['sent_hashes']:
            dept_data['sent_hashes'].append(announcement_hash)
            dept_data['last_titles'].append(title)
            
            # Keep only last 50 entries to prevent unlimited growth
            if len(dept_data['sent_hashes']) > 50:
                dept_data['sent_hashes'] = dept_data['sent_hashes'][-50:]
                dept_data['last_titles'] = dept_data['last_titles'][-50:]
            
            self._save_data()


if __name__ == "__main__":
    # Test the database handler
    db = DatabaseHandler("test_data/bot_data.json")
    
    # Test user operations
    db.add_user_subscription(12345, "test_user", "Bilgisayar Mühendisliği")
    db.add_user_subscription(12346, "test_user2", "Yapay Zeka Mühendisliği")
    
    # Test announcement tracking
    db.mark_announcement_sent("Bilgisayar Mühendisliği", "hash123", "Test Announcement")
    
    print("Database stats:", db.get_stats())
    print("Users for Bilgisayar Mühendisliği:", db.get_users_by_department("Bilgisayar Mühendisliği"))
