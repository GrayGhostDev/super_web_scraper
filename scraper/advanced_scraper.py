from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup
import random
import time
import logging
from typing import Dict, Any, Optional
from .config import (
    HEADERS, USER_AGENTS, SELENIUM_WAIT_TIME,
    SCROLL_PAUSE_TIME, MAX_RETRIES, TIMEOUT
)

logger = logging.getLogger(__name__)

class AdvancedScraper:
    def __init__(self):
        self.session = requests.Session()
        self._setup_session()
        self.driver = None

    def _setup_session(self):
        """Configure requests session with default headers and rotation."""
        self.session.headers.update(HEADERS)
        self.session.headers['User-Agent'] = random.choice(USER_AGENTS)

    def _get_chrome_options(self) -> Options:
        """Configure Chrome options for Selenium."""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'user-agent={random.choice(USER_AGENTS)}')
        options.add_argument('--disable-javascript')  # Optional: disable JS for faster loading
        return options

    def _setup_driver(self) -> webdriver.Chrome:
        """Set up Chrome WebDriver with managed driver installation."""
        try:
            service = Service(ChromeDriverManager().install())
            options = self._get_chrome_options()
            return webdriver.Chrome(service=service, options=options)
        except Exception as e:
            logger.error(f"Error setting up WebDriver: {str(e)}")
            raise

    def scrape_with_selenium(self, url: str) -> Optional[str]:
        """Scrape website using Selenium for JavaScript-rendered content."""
        try:
            if not self.driver:
                self.driver = self._setup_driver()
            
            self.driver.get(url)
            WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            self._scroll_page(self.driver)
            return self.driver.page_source
            
        except TimeoutException:
            logger.error(f"Timeout while loading {url}")
            return None
        except Exception as e:
            logger.error(f"Error scraping with Selenium: {str(e)}")
            return None
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None

    def _scroll_page(self, driver):
        """Scroll the page to load dynamic content."""
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def scrape_with_requests(self, url: str) -> Optional[str]:
        """Scrape website using requests library."""
        try:
            response = self.session.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error scraping with requests: {str(e)}")
            return None

    def scrape(self, url: str, method: str = "selenium", save_file: Optional[str] = None) -> Dict[str, Any]:
        """Main method to scrape a website with retry mechanism."""
        html = None
        retries = 0
        
        while retries < MAX_RETRIES and not html:
            try:
                if method == "selenium":
                    html = self.scrape_with_selenium(url)
                else:
                    html = self.scrape_with_requests(url)
                
                if not html:
                    retries += 1
                    time.sleep(1)
                    continue
                
                data = self._extract_content(html, url)
                
                if save_file:
                    self._save_to_file(data, save_file)
                
                return data
                
            except Exception as e:
                logger.error(f"Error during scraping attempt {retries + 1}: {str(e)}")
                retries += 1
                time.sleep(1)
        
        raise Exception(f"Failed to scrape {url} after {MAX_RETRIES} attempts")

    def _extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """Extract and structure content from HTML."""
        soup = BeautifulSoup(html, 'lxml')
        
        return {
            'url': url,
            'title': soup.title.string if soup.title else None,
            'content': soup.get_text(strip=True),
            'links': [a.get('href') for a in soup.find_all('a', href=True)]
        }

    def _save_to_file(self, data: Dict[str, Any], filename: str):
        """Save scraped data to file."""
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)