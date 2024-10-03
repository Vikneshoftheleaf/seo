import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import os


def save_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
        


def extract_domain_name(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    domain_with_protocol = f"{parsed_url.scheme}://{domain}"
    return domain_with_protocol



def is_https(url):
    return url.startswith("https://")

# Function to check if robots.txt exists
def has_robots_txt(domain):
    robots_url = domain + "/robots.txt"
    try:
        response = requests.get(robots_url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Function to check if sitemap.xml exists
def has_sitemap_xml(domain):
    sitemap_url = domain + "/sitemap.xml"
    try:
        response = requests.get(sitemap_url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Function to measure page load speed
def get_page_load_speed(url):
    start_time = time.time()
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            load_time = time.time() - start_time
            return load_time
        else:
            return None
    except requests.RequestException:
        return None


def check_broken_link(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)  # Using head request to check the link
        if response.status_code >= 400:
            return True  # Link is broken
        return False
    except requests.exceptions.RequestException:
        return True  # If any exception occurs, we consider the link broken



#export function
def getInfo(current_url):
    try:
        response = requests.get(current_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else False

            # Extract meta description
            meta_description = False
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag and 'content' in meta_tag.attrs:
                meta_description = meta_tag['content']
            
            # Extract favicon link
            favicon = False
            icon_link = soup.find('link', rel=lambda value: value and 'icon' in value.lower())
            #icon_link = soup.find('link', rel=lambda x: x and 'icon' in x)
            if icon_link and 'href' in icon_link.attrs:
                favicon = urljoin(current_url, icon_link['href'])
            

            # Extract all headings
            headings = {
                'h1': [h1.get_text(strip=True) for h1 in soup.find_all('h1')],
                'h2': [h2.get_text(strip=True) for h2 in soup.find_all('h2')],
                'h3': [h3.get_text(strip=True) for h3 in soup.find_all('h3')],
                'h4': [h4.get_text(strip=True) for h4 in soup.find_all('h4')],
                'h5': [h5.get_text(strip=True) for h5 in soup.find_all('h5')],
                'h6': [h6.get_text(strip=True) for h6 in soup.find_all('h6')]
            }
            
            # Extract Content
            text_content = soup.get_text(separator=' ', strip=True)
            cleaned_text = ' '.join(text_content.split())
            word_count = len(cleaned_text.split())
            
            #Extract Images Information
            images = soup.find_all('img')
            total_images = len(images)
            images_without_alt = 0
            
            for img in images:
                if not img.has_attr('alt') or not img['alt'].strip():  # Check if alt is missing or empty
                    images_without_alt += 1
                    
                    
                    
            # Extract Links
            links = soup.find_all('a', href=True)
    
            internal_links = []
            external_links = []
            broken_links = []
            
            domain = urlparse(current_url).netloc
            
            for link in links:
                href = link['href']
                full_url = urljoin(current_url, href)
                
                # Check if the link is internal or external
                if domain in urlparse(full_url).netloc:
                    internal_links.append(full_url)
                else:
                    external_links.append(full_url)
                
                if check_broken_link(full_url):
                    broken_links.append(full_url)
            

            # Store crawled data
            crawled_data = {
                'url': current_url,
                'domain': extract_domain_name(current_url),
                'title': title,
                'meta_description': meta_description,
                'favicon': favicon,
                'headings': headings,
                'text_content':text_content,
                'words_count': word_count,
                'ssl': is_https(current_url),
                'robots_txt': has_robots_txt(extract_domain_name(current_url)),
                'sitemap_xml': has_sitemap_xml(extract_domain_name(current_url)),
                'page_load_speed': get_page_load_speed(current_url),
                "total_images":total_images,
                "imgWithoutAlt": images_without_alt,
                "total_links": len(links),
                "internal_links": internal_links,
                "external_links": external_links,
                "broken_links": broken_links

            }
            #save_json('test.json', crawled_data)
            
            return crawled_data

        
    except requests.RequestException as e:
        print(f"Failed to crawl {current_url}: {e}")
        return False
