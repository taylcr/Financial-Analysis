from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time

def fetch_html_with_selenium(url):
    # Set up Firefox options
    options = Options()
    options.headless = True  # Run in headless mode (without opening a window)

    # Create a service object and initialize the driver
    service = Service('/path/to/geckodriver')  # Adjust the path to geckodriver
    driver = webdriver.Firefox(service=service, options=options)

    try:
        # Open the URL
        driver.get(url)
        time.sleep(5)  # Wait for the page to load fully

        # Retrieve the page's HTML
        html_content = driver.page_source
        print("HTML content retrieved successfully!")
        return html_content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        driver.quit()  # Close the browser

if __name__ == "__main__":
    url = 'https://x.com/search?q=elon%20musk&src=typed_query'
    html_content = fetch_html_with_selenium(url)
    
    if html_content:
        print(html_content)  # Print the HTML content for testing
