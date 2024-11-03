import requests
from bs4 import BeautifulSoup
from googlesearch import search
import csv
from uploading import upload

def sanitize_filename(url):
    valid_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(c if c in valid_chars else '_' for c in url)

def save_web_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text(separator='\n', strip=True)

        return text_content

    except requests.RequestException as e:
        print(f"Failed to retrieve {url}: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def web_scrape(topic):
    query = topic
    urls = [j for j in search(query)]

    with open('urls_content.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['url', 'content']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for url in urls:
            content = save_web_content(url)
            if content is not None:
                writer.writerow({'url': url, 'content': content})
    upload()
    print("All URLs and content saved to urls_content.csv and uploaded to AWS.")

# Add a main function to call this from another script
def run_crawler(input):
    web_scrape(input)  # Modify the topic as needed
