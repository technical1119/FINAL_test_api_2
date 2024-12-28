import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

import time

import json


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


def get_social_links_from_overview(url):
    req = requests.get(url)
    if req.status_code == 200:
        try:    
            soup = BeautifulSoup(req.text, "html.parser")
            next_data = soup.find("script", {"id": "__NEXT_DATA__"})
            data = json.loads(next_data.string)
            links = data["props"]["pageProps"]['coin']['links']
            print(links)
        except:
            print("No links found")
            return None

    else:
        print(f"Failed to retrieve the page. Status code: {req.status_code}")
        return None
    return links


def get_links_from_webpage(url):

    links = []

    headers = {
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }

    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        bs = BeautifulSoup(response.content, 'html.parser')
    
        a_objects = bs.find_all('a')
        for a in a_objects:
            href = a.get('href')
            if href:
                if "https://" in href or "http://" in href:
                    links.append(href)
                else: 
                    links.append(url + href)

        print(len(links))
        return links
    else:
        print(f"Failed to fetch URL: {url}. Status code: {response.status_code}")
        return None


def get_website_content_http(url):

    return_content = str()
  
    headers = {
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        first_layer_links = get_links_from_webpage(url)
        if first_layer_links:
            first_layer_links.append(url)
            for link in first_layer_links:
                if url in link:
                    print("Getting content from: ", link, "\n")
                    response = requests.get(link, headers=headers)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        print("adding text with length: ", len(soup.get_text()), "\n")
                        return_content += soup.get_text() + " "       
        return return_content
    else:
        print(f"Failed to fetch URL: {url}. Status code: {response.status_code}")
        return None
    


def get_links_from_webpage_Selenum(url):
    links = []
    

    try:
        # Initialize the driver
        driver = create_webdirver()
        
        # Get the page
        driver.get(url)
        time.sleep(2)
        # Find all anchor elements
        a_elements = driver.find_elements(By.TAG_NAME, 'a')
        print(len(a_elements))
        # Extract href attributes
        for a in a_elements:
            href = a.get_attribute('href')
            if href:
                if "https://" in href or "http://" in href:
                    links.append(href)
                else:
                    links.append(url + href)
        
        print(len(links))
        return links
        
    except Exception as e:
        print(f"Error getting links with Selenium: {e}")
        return None
        
    finally:
        # Always close the driver
        driver.quit()




def get_website_content_selenium(url):
    return_content = str()
    
  
    driver = create_webdirver()
    
    try:
        driver.get(url)
        first_layer_links = get_links_from_webpage_Selenum(url)  # Reuse existing function
        print(len(first_layer_links))
        if first_layer_links:
            first_layer_links.append(url)
            for link in first_layer_links:
                if url in link:
                    print("Getting content from: ", link, "\n")
                    driver.get(link)
                    
                    # Get page content
                    page_content = driver.page_source
                    soup = BeautifulSoup(page_content, 'html.parser')
                    print("adding text with length: ", len(soup.get_text()), "\n")
                    return_content += soup.get_text() + " "
                    
        return return_content
        
    except Exception as e:
        print(f"Error accessing URL: {url}. Error: {str(e)}")
        return None
        
    finally:
        driver.quit()



print(get_website_content_selenium("https://www.swanchain.io/"))


