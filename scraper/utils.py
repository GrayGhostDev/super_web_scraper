import re
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
import json
import logging
from bs4 import BeautifulSoup
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    # Remove extra whitespace and normalize line endings
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text

def extract_metadata(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """Extract metadata from the webpage."""
    metadata = {
        'url': url,
        'timestamp': datetime.now().isoformat(),
        'title': soup.title.string if soup.title else None,
        'meta_description': None,
        'meta_keywords': None,
        'canonical_url': None,
        'language': None
    }
    
    # Extract meta description
    meta_desc = soup.find('meta', {'name': 'description'})
    if meta_desc:
        metadata['meta_description'] = meta_desc.get('content')
    
    # Extract meta keywords
    meta_keywords = soup.find('meta', {'name': 'keywords'})
    if meta_keywords:
        metadata['meta_keywords'] = meta_keywords.get('content')
    
    # Extract canonical URL
    canonical = soup.find('link', {'rel': 'canonical'})
    if canonical:
        metadata['canonical_url'] = canonical.get('href')
    
    # Extract language
    html_tag = soup.find('html')
    if html_tag:
        metadata['language'] = html_tag.get('lang')
    
    return metadata

def extract_links(soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
    """Extract and normalize all links from the webpage."""
    links = []
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        text = clean_text(link.get_text())
        if href:
            absolute_url = urljoin(base_url, href)
            if is_valid_url(absolute_url):
                links.append({
                    'url': absolute_url,
                    'text': text,
                    'type': 'internal' if is_same_domain(base_url, absolute_url) else 'external'
                })
    return links

def is_valid_url(url: str) -> bool:
    """Check if a URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def is_same_domain(url1: str, url2: str) -> bool:
    """Check if two URLs belong to the same domain."""
    domain1 = urlparse(url1).netloc
    domain2 = urlparse(url2).netloc
    return domain1 == domain2

def save_to_json(data: Dict[str, Any], filename: str) -> None:
    """Save scraped data to a JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Data saved successfully to {filename}")
    except Exception as e:
        logger.error(f"Error saving data to {filename}: {str(e)}")

def extract_structured_data(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract structured data (JSON-LD) from the webpage."""
    structured_data = []
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string)
            structured_data.append(data)
        except Exception as e:
            logger.warning(f"Error parsing structured data: {str(e)}")
    return structured_data