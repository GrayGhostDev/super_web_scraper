import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import random
import time

# List of user agents for rotation
user_agents_list = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

def get_chrome_options(user_agent=None):
    """Configure Chrome options for Selenium."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if user_agent:
        options.add_argument(f'user-agent={user_agent}')
    return options

def scrape_website(website, method="Selenium", user_agent="Default", timeout=10):
    """Scrape website content using either Selenium or Requests."""
    if user_agent == "Rotate":
        user_agent = random.choice(user_agents_list)
    elif user_agent == "Default":
        user_agent = None

    try:
        if method == "Selenium":
            options = get_chrome_options(user_agent)
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(timeout)
            driver.get(website)
            html_content = driver.page_source
            driver.quit()
            return html_content
        
        elif method == "Requests":
            headers = {'User-Agent': user_agent} if user_agent else {}
            response = requests.get(website, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.text
        
        else:
            raise ValueError("Invalid scraping method selected.")
            
    except Exception as e:
        raise Exception(f"Failed to scrape website: {str(e)}")

def extract_body_content(html_content):
    """Extract the body content from HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.body.get_text() if soup.body else ""

def clean_body_content(content):
    """Clean the extracted content."""
    # Remove extra whitespace and normalize line endings
    content = " ".join(content.split())
    return content

def split_dom_content(content, chunk_size=1000):
    """Split content into chunks for parsing."""
    words = content.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        word_size = len(word) + 1  # +1 for space
        if current_size + word_size > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_size = word_size
        else:
            current_chunk.append(word)
            current_size += word_size
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks