# CHROMEDRIVER_PATH = 'C:/chromedriver/chromedriver-win64/chromedriver.exe'  # Ensure this points to chromedriver.exe on Windows
from flask_scss import Scss
from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import logging

app = Flask(__name__)

# Path to your chromedriver
CHROMEDRIVER_PATH = 'C:/chromedriver/chromedriver-win64/chromedriver.exe'  # Ensure this points to chromedriver.exe on Windows

# Web scraping function for Medium using Selenium
def scrape_medium(query='education'):
    options = Options()
    options.add_argument("--headless")  # Ensure headless mode is enabled
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")  # Disable GPU for headless mode
    service = ChromeService(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    
    url = f'https://medium.com/search?q={query}'
    driver.get(url)

    # Wait for the page to load
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    articles = soup.find_all('article')

    article_data = []
    for article in articles:
        title_tag = article.find('h2')
        description_tag = article.find('h3')
        if title_tag:
            title = title_tag.text.strip()
            description = description_tag.text.strip() if description_tag else "No description available"
            article_data.append({'title': title, 'description': description})

    return article_data

# Web scraping function for YouTube using Selenium
def scrape_youtube(query='education'):
    options = Options()
    options.add_argument("--headless")  # Ensure headless mode is enabled
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")  # Disable GPU for headless mode
    service = ChromeService(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    
    url = f'https://www.youtube.com/results?search_query={query}'
    driver.get(url)

    # Wait for the search results to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "contents"))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    videos = soup.find_all('ytd-video-renderer', class_='style-scope ytd-item-section-renderer')

    video_data = []
    for video in videos:
        title_tag = video.find('a', id='video-title')
        description_tag = video.find('yt-formatted-string', class_='style-scope ytd-video-renderer')
        if title_tag:
            title = title_tag.text.strip()
            url = f"https://www.youtube.com{title_tag['href']}"
            description = description_tag.text.strip() if description_tag else "No description available"
            video_data.append({'title': title, 'description': description, 'url': url})

    return video_data


# Web scraping function for ResearchGate using Selenium
def scrape_researchgate(query='education'):
    options = Options()
    options.add_argument("--headless")  # Ensure headless mode is enabled
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")  # Disable GPU for headless mode
    service = ChromeService(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    
    url = f'https://www.researchgate.net/search/publication?q={query}'
    driver.get(url)

    # Wait for the search results to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "search-result-item"))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    papers = soup.find_all('div', class_='search-result-item')

    paper_data = []
    for paper in papers:
        title_tag = paper.find('div', class_='nova-legacy-e-text--color-inherit')
        if title_tag:
            title = title_tag.text.strip()
            url_tag = paper.find('a', class_='nova-legacy-e-link')
            url = f"https://www.researchgate.net{url_tag['href']}" if url_tag else '#'
            description = "No description available"
            paper_data.append({'title': title, 'description': description, 'url': url})

    return paper_data

# Web scraping function for ScienceDirect using Selenium
def scrape_sciencedirect(query='education'):
    options = Options()
    options.add_argument("--headless")  # Ensure headless mode is enabled
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")  # Disable GPU for headless mode
    service = ChromeService(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    
    url = f'https://www.sciencedirect.com/search?qs={query}'
    driver.get(url)

    try:
        # Increase the timeout to 20 seconds
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "result-list-title-link"))
        )
    except TimeoutException:
        logging.error("Timeout while waiting for search results to load on ScienceDirect")
        driver.quit()
        return []

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    papers = soup.find_all('h2', class_='result-list-title')
    print(soup.prettify())

    paper_data = []
    for paper in papers:
        title_tag = paper.find('a')
        if title_tag:
            title = title_tag.text.strip()
            url = f"https://www.sciencedirect.com{title_tag['href']}"
            description = "No description available"
            paper_data.append({'title': title, 'description': description, 'url': url})

    return paper_data


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    source = request.form['source']
    if source == 'medium':
        article_data = scrape_medium(query)
    elif source == 'youtube':
        article_data = scrape_youtube(query)
    elif source == 'researchgate':
        article_data = scrape_researchgate(query)
    elif source == 'sciencedirect':
        article_data = scrape_sciencedirect(query)
    else:
        article_data = []
    return jsonify(article_data)

if __name__ == '__main__':
    app.run(debug=True)
