from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

import time 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def create_webdirver():
    # Replace with your Railway URL
    REMOTE_URL = "https://standalone-chrome-production-c37d.up.railway.app"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36"
    }
    # Set up Chrome options
    options = Options()
    options.add_argument(f'user-agent={headers["User-Agent"]}')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Connect to remote WebDriver
    driver = webdriver.Remote(
        command_executor=REMOTE_URL,
        options=options
    )

    return driver
    


def get_page_source(url, timeout=10):
    driver = create_webdirver()
    if driver is None:
        raise Exception("Failed to create Chrome driver")
        
    try:
        driver.set_window_size(1920, 1080)
        driver.get(url)
        return driver.page_source
    except Exception as e:
        print(f"Error getting page source: {e}")
        return None
    finally:
        driver.quit()


def get_defilama_projects():
    projects = []
    page_source = get_page_source("https://defillama.com/recent")
    soup = BeautifulSoup(page_source, "html.parser")
    table_container = soup.find("div", id = "table-wrapper").find_all("a", class_ = "text-sm font-medium text-[var(--link-text)] overflow-hidden whitespace-nowrap text-ellipsis hover:underline")
    if table_container:
        if len(table_container) > 0:        
            for i in table_container:
                name  = i.text
                link = "https://defillama.com" + i.get("href")
                projects.append({"name": name, "link": link})
            return projects
        else:
            return None
    else:
        return None
    


def get_defilama_project_details(url):
    social_links = []
    driver = create_webdirver()
    time.sleep(5)
    driver.set_window_size(1920, 1080)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    try:
        # Navigate to the page
        driver.get(url)
        

        social_block = driver.find_element(By.XPATH, "//*[@id='__next']/main/div/div[2]/div[2]/div[1]/div")
        
        social_data = social_block.find_elements(By.TAG_NAME, "a")
        
        for link in social_data:
            social_name = link.find_element(By.TAG_NAME, "span").get_property("textContent")
            social_link = link.get_attribute("href")
            if social_link:  # Only add if there's actually a link
                    social_links.append({
                        "name": social_name,
                        "link": social_link
                    })

        return social_links
    except Exception as e:
        print(f"Error getting page source: {e}")
        return None
    finally:
        # Always close the driver
        driver.quit()
    return social_links


print(get_defilama_projects())