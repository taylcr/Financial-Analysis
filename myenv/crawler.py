import requests
from bs4 import BeautifulSoup
from googlesearch import search
import os
import csv

def sanitize_filename(url):
    valid_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(c if c in valid_chars else '_' for c in url)

def save_web_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text(separator='\n', strip=True)

        return text_content  # Return the text content

    except requests.RequestException as e:
        print(f"Failed to retrieve {url}: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    query = "Geeksforgeeks"
    urls = [j for j in search(query)]

    # Save URLs and content to a CSV file
    with open('urls_content.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['url', 'content']  # Add content as a field
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()  # Write the header

        for url in urls:
            content = save_web_content(url)  # Retrieve the content
            if content is not None:  # Only save if content retrieval was successful
                writer.writerow({'url': url, 'content': content})  # Write the URL and content to the CSV

    print("All URLs and content saved to urls_content.csv.")
