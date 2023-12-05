import os
import pandas as pd
import selenium
from packaging import version
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Check the installed Selenium version
installed_selenium_version = selenium.__version__

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ensure GUI is off
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--disable-gpu')


global last_update_time
global database


def update_table(url, local_path):
    # Use the appropriate method to initialize the Chrome driver based on Selenium version
    if version.parse(installed_selenium_version) > version.parse("3.141.0"):
        # For newer versions of Selenium
        from selenium.webdriver.chrome.service import Service
        webdriver_service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    else:
        # For older versions of Selenium
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

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
    else:
        print('Table not found')

    # Clean up (close the browser)
    driver.quit()


def parse_html(file_path):
    # Since the format of the data in the file is unknown, I will first open the file and read its content to understand its structure.
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Using BeautifulSoup to parse the HTML content
    soup = BeautifulSoup("".join(lines), 'html.parser')

    # Finding all rows in the table
    rows = soup.find_all('tr')

    # Define a function to extract text from a tag, stripping and replacing unwanted characters
    def extract_text(tag):
        text = tag.get_text(strip=True)
        if '%' in text:
            return text.split('%')[0]
        elif '#' in text:
            return text.replace('#', '')
        elif '-' in text:
            raise AttributeError
        elif '돌격 소총' in text:
            text = text.replace('돌격 소총', '돌격소총')
        return text

    # Parsing each row
    data = []
    for row in rows:
        # Finding all cells in the row
        cells = row.find_all('td')
        if len(cells) > 1:  # Making sure it's not a header or empty row
            try:
                # Extracting data from each cell
                character_name = extract_text(cells[1])  # Character name
                rp_gain = float(extract_text(cells[2]))  # RP Gain
                pick_rate = float(extract_text(cells[3]))  # Pick Rate
                win_rate = float(extract_text(cells[4]))  # Win Rate
                top_3 = float(extract_text(cells[5]))  # TOP 3
                average_rank = float(extract_text(cells[6]))  # Average Rank
                damage = int(extract_text(cells[7]).replace(',', ''))  # Damage
                average_tk = float(extract_text(cells[8]))  # Average TK
                player_kills = float(extract_text(cells[9]))  # Player Kills
                animal_kills = float(extract_text(cells[10]))  # Animal Kills

                # Adding the extracted data to the list
                data.append([character_name, rp_gain, pick_rate, win_rate, top_3, average_rank, damage, average_tk, player_kills, animal_kills, 100 * (win_rate / top_3)])
            except AttributeError:
                continue

    # Creating a DataFrame from the parsed data
    columns = ['Character', 'RP Gain', 'Pick Rate', 'Win Rate', 'TOP 3', 'Average Rank', 'Damage', 'Average TK', 'Player Kills', 'Animal Kills', 'Win Rate / Top 3']
    df = pd.DataFrame(data, columns=columns)
    return df


def update_table_all():
    from config import url_mapping
    basepath = "data/"

    for key, url in url_mapping.items():
        update_table(url, os.path.join(basepath, f"{str(key)}.html"))


# 전역변수 database 갱신 함수
def update_database():
    from config import url_mapping
    global database
    database_ = {}
    for key, url in url_mapping.items():
        tier, version = key
        database_[key] = parse_html(os.path.join('data', f"('{tier}', '{version}').html"))
    database = database_


def update_last_time():
    from datetime import datetime
    import pytz
    global last_update_time
    # 현재 시간을 UTC+9 시간대로 변환
    tz = pytz.timezone('Asia/Tokyo')  # UTC+9 시간대
    now = datetime.now(tz)

    # 형식에 맞게 시간을 문자열로 변환
    time_str = now.strftime("%Y/%m/%d %H:%M UTC+9")
    last_update_time = time_str

    # 파일에 기록
    with open('data/last_update_time.txt', 'w', encoding='utf-8') as f:
        f.write(time_str)


# update_table을 주기적으로 실행하는 함수
def run_periodic_update():
    import time
    while True:
        time.sleep(10800)  # 3시간 대기 (3시간 = 10800초)
        update_table_all()
        update_database()
        update_last_time()


def get_last_update_time():
    return last_update_time

def get_database():
    return database



if __name__ == '__main__':
    update_table_all()
