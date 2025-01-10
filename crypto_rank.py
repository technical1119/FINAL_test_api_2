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

from urllib.parse import urlparse
import time

import json
import asyncio


SOCIAL_MEDIA_DOMAINS = [
    "x.com",
    "t.me",  # Telegram
    "medium.com",
    "discord.gg",
    "discord.com",
    "linkedin.com",
    "reddit.com",
    "youtube.com",
    "facebook.com",
    "instagram.com",
    "tiktok.com",
    
]

async def create_webdriver():
    REMOTE_URL = "https://standalone-chrome-production-9ee2.up.railway.app"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36"
    }
    options = Options()
    options.add_argument(f'user-agent={headers["User-Agent"]}')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: webdriver.Remote(
            command_executor=REMOTE_URL,
            options=options
        )
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
        # remove  duplicates 
        links = list(set(links))
        print(links)
        # remove social links 
        for link in links:
            if any(domain in link for domain in SOCIAL_MEDIA_DOMAINS):
                links.remove(link)
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
    


async def get_links_from_webpage_Selenium(url):
    
    links = []
    driver = await create_webdriver()
    
    try:
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: driver.get(url)
        )
        await asyncio.sleep(2)

        a_elements = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: driver.find_elements(By.TAG_NAME, 'a')
        )
        
        for a in a_elements:
            href = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: a.get_attribute('href')
            )
            if href:
                if "https://" in href or "http://" in href:
                    links.append(href)
                else:
                    links.append(url + href)
        # remove  duplicates 
        links = list(set(links))
        print(links)
        # remove social links 
        for link in links:
            if any(domain in link for domain in SOCIAL_MEDIA_DOMAINS):
                links.remove(link)
        return links
    except Exception as e:
        print(f"Error getting links with Selenium: {e}")
        return None
    finally:
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: (driver.close(), driver.quit())
        )


async def get_website_content_selenium(url):
    return_content = str()
    first_layer_links = await get_links_from_webpage_Selenium(url)
    driver = await create_webdriver()
    print(first_layer_links)
    try:
        if first_layer_links:
            print("some links found")
            first_layer_links.append(url)
            for link in first_layer_links:
                link_domain = urlparse(link).netloc
                print(link_domain)
                if link_domain in url:
                    print("Getting content from: ", link, "\n")
                    await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: driver.get(link)
                    )
                    
                    page_content = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: driver.page_source
                    )
                    soup = BeautifulSoup(page_content, 'html.parser')
                    print("adding text with length: ", len(soup.get_text()), "\n")
                    return_content += soup.get_text() + " "
        return return_content
    except Exception as e:
        print(f"Error accessing URL: {url}. Error: {str(e)}")
        return None
    finally:
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: (driver.close(), driver.quit())
        )
        
async def get_page_content_selenium(list_of_urls):
    print(type(list_of_urls))
    return_content = str()
    if len(list_of_urls) > 0:
        driver = await create_webdriver()
        try:
           
            for link in list_of_urls:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: driver.get(link)
                )
                        
                page_content = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: driver.page_source
                )

                soup = BeautifulSoup(page_content, 'html.parser')
                print("adding text with length: ", len(soup.get_text()), "\n")
                return_content += soup.get_text() + " "

            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: (driver.close(), driver.quit())
            )
            return return_content
        except Exception as e:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: (driver.close(), driver.quit())
            )
            return None
    
    else:
        return None
    
        




    
        

        


