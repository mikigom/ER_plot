import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ensure GUI is off
chrome_options.add_argument("--no-sandbox")


def update_table(url, local_path):
    # Set path to chromedriver as per your configuration
    webdriver_service = Service(ChromeDriverManager().install())

    # Choose Chrome Browser
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

    # WebDriver will wait for a page to load by default. Let's make sure we wait for JavaScript to load.
    driver.get(url)

    # Wait for the necessary element to load on the page
    driver.implicitly_wait(100)  # You can adjust the wait time as per the page's response time.

    # Now that the page is fully loaded, grab the page source.
    html = driver.page_source

    # Parse the HTML content of the page using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Find the table with the specific class
    table = soup.find('table', {'class': 'w-full text-[12px]'})

    # Save the table to an HTML file
    if table:
        with open(local_path, 'w', encoding='utf-8') as file:
            file.write(str(table))
        print("Table saved to table.html")
    else:
        print('Table not found')

    # Clean up (close the browser)
    driver.quit()


def main():
    from config import url_mapping
    basepath = "data/"

    for key, url in url_mapping.items():
        update_table(url, os.path.join(basepath, f"{str(key)}.html"))


if __name__ == '__main__':
    main()
