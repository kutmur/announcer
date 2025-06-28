"""
Web scraper for BTU department announcements
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional
import time
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnnouncementScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_announcements(self, url: str, max_announcements: int = 5) -> List[Dict]:
        """
        Scrape announcements from a BTU department page
        
        Args:
            url: Department announcement page URL
            max_announcements: Maximum number of announcements to fetch
            
        Returns:
            List of announcement dictionaries with title, link, date, and description
        """
        try:
            logger.info(f"Scraping announcements from: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            announcements = []
            
            # Look for announcement patterns specific to BTU
            # Method 1: Find date + link patterns
            announcement_elements = []
            
            # BTU uses this pattern: [date] [announcement text](link)
            # Let's find all links that contain "/duyuru/detay/"
            detail_links = soup.find_all('a', href=lambda href: href and '/duyuru/detay/' in href)
            
            if detail_links:
                logger.info(f"Found {len(detail_links)} announcement detail links")
                
                for link in detail_links[:max_announcements]:
                    try:
                        announcement = self._extract_btu_announcement(link, url)
                        if announcement and announcement['title'].strip():
                            announcements.append(announcement)
                    except Exception as e:
                        logger.warning(f"Error extracting BTU announcement: {e}")
                        continue
            
            # If we didn't get announcements from detail links, try other methods
            if not announcements:
                # Try original selectors as fallback
                announcement_selectors = [
                    '.duyuru-item',
                    '.news-item',
                    '.announcement-item',
                    'article',
                    '.list-group-item',
                    'tr',
                ]
                
                for selector in announcement_selectors:
                    elements = soup.select(selector)
                    if elements:
                        logger.info(f"Fallback: Found {len(elements)} elements with selector: {selector}")
                        
                        for element in elements[:max_announcements]:
                            try:
                                announcement = self._extract_announcement_data(element, url)
                                if announcement and announcement['title'].strip():
                                    announcements.append(announcement)
                            except Exception as e:
                                logger.warning(f"Error extracting announcement data: {e}")
                                continue
                        
                        if announcements:
                            break
            
            logger.info(f"Successfully scraped {len(announcements)} announcements")
            return announcements
            
        except requests.RequestException as e:
            logger.error(f"Network error scraping {url}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            return []
    
    def _extract_btu_announcement(self, link_element, base_url: str) -> Optional[Dict]:
        """
        Extract announcement data from BTU-specific link element
        
        Args:
            link_element: BeautifulSoup link element
            base_url: Base URL for resolving relative links
            
        Returns:
            Dictionary with announcement data or None if extraction fails
        """
        try:
            announcement = {
                'title': '',
                'link': '',
                'date': '',
                'description': '',
                'hash': ''
            }
            
            # Extract link
            href = link_element.get('href')
            if href:
                announcement['link'] = urljoin(base_url, href)
            
            # Extract title from link text
            title_text = link_element.get_text().strip()
            if title_text:
                announcement['title'] = title_text
            
            # Try to find date in the previous text or parent element
            # BTU format is usually [DD.MM.YYYY Title]
            parent = link_element.parent
            if parent:
                parent_text = parent.get_text()
                
                # Look for date pattern before the link text
                import re
                date_pattern = r'(\d{2}\.\d{2}\.\d{4})'
                date_match = re.search(date_pattern, parent_text)
                
                if date_match:
                    announcement['date'] = date_match.group(1)
                    
                    # Clean up title by removing date if it's at the beginning
                    clean_title = parent_text.replace(announcement['date'], '').strip()
                    if clean_title and len(clean_title) > 5:  # Use cleaned title if meaningful
                        announcement['title'] = clean_title
            
            # Create hash for duplicate detection
            hash_content = f"{announcement['title']}{announcement['link']}"
            announcement['hash'] = str(hash(hash_content))
            
            # Return if we have at least a title
            if announcement['title'] and len(announcement['title']) > 3:
                return announcement
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting BTU announcement: {e}")
            return None
    
    def _extract_announcement_data(self, element, base_url: str) -> Optional[Dict]:
        """
        Extract announcement data from a single element
        
        Args:
            element: BeautifulSoup element containing announcement
            base_url: Base URL for resolving relative links
            
        Returns:
            Dictionary with announcement data or None if extraction fails
        """
        try:
            announcement = {
                'title': '',
                'link': '',
                'date': '',
                'description': '',
                'hash': ''
            }
            
            # Extract title
            title_element = None
            
            # Try different ways to find the title
            title_selectors = ['h3', 'h4', 'h5', '.title', '.announcement-title', 'a']
            
            for selector in title_selectors:
                title_element = element.select_one(selector)
                if title_element and title_element.get_text().strip():
                    break
            
            if not title_element:
                # If element itself is a link, use its text
                if element.name == 'a':
                    title_element = element
                else:
                    # Use the element's text directly
                    announcement['title'] = element.get_text().strip()
            
            if title_element:
                announcement['title'] = title_element.get_text().strip()
            
            # Extract link
            link_element = element.find('a') if element.name != 'a' else element
            if link_element and link_element.get('href'):
                href = link_element.get('href')
                announcement['link'] = urljoin(base_url, href)
            
            # Extract date
            date_selectors = ['.date', '.announcement-date', '.publish-date', 'time', '.tarih']
            for selector in date_selectors:
                date_element = element.select_one(selector)
                if date_element:
                    announcement['date'] = date_element.get_text().strip()
                    break
            
            # Extract description/content preview
            desc_selectors = ['.description', '.content', '.summary', 'p']
            for selector in desc_selectors:
                desc_element = element.select_one(selector)
                if desc_element:
                    desc_text = desc_element.get_text().strip()
                    if desc_text and desc_text != announcement['title']:
                        announcement['description'] = desc_text[:200] + "..." if len(desc_text) > 200 else desc_text
                        break
            
            # Create a hash for duplicate detection
            hash_content = f"{announcement['title']}{announcement['link']}"
            announcement['hash'] = str(hash(hash_content))
            
            # Only return if we have at least a title
            if announcement['title']:
                return announcement
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting announcement data: {e}")
            return None
    
    def test_scraping(self, url: str) -> bool:
        """
        Test if scraping works for a given URL
        
        Args:
            url: URL to test
            
        Returns:
            True if scraping successful, False otherwise
        """
        try:
            announcements = self.scrape_announcements(url, max_announcements=1)
            return len(announcements) > 0
        except Exception as e:
            logger.error(f"Test scraping failed for {url}: {e}")
            return False


# Example usage and testing
if __name__ == "__main__":
    scraper = AnnouncementScraper()
    
    # Test with a few URLs
    test_urls = [
        "https://mdbf.btu.edu.tr/tr/bilgisayar/duyuru/birim/193",
        "https://mdbf.btu.edu.tr/tr/yapayzeka/duyuru/birim/10334"
    ]
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        announcements = scraper.scrape_announcements(url, max_announcements=3)
        
        if announcements:
            print(f"Found {len(announcements)} announcements:")
            for i, ann in enumerate(announcements, 1):
                print(f"{i}. {ann['title']}")
                print(f"   Link: {ann['link']}")
                print(f"   Date: {ann['date']}")
                if ann['description']:
                    print(f"   Description: {ann['description']}")
                print()
        else:
            print("No announcements found")
