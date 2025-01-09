import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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

    # Run in executor to avoid blocking
    driver = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: webdriver.Remote(
            command_executor=REMOTE_URL,
            options=options
        )
    )
    await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: driver.set_window_size(1920, 1080)
    )
    return driver

async def get_page_source(url, timeout=10):
    driver = await create_webdriver()
    if driver is None:
        raise Exception("Failed to create Chrome driver")
        
    try:
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: driver.get(url)
        )
        await asyncio.sleep(2)  # Non-blocking sleep
        page_content = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: driver.page_source
        )
        return page_content
    except Exception as e:
        print(f"Error getting page source: {e}")
        return None
    finally:
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: (driver.close(), driver.quit())
        )

async def get_defilama_projects():
    projects = []
    page_source = await get_page_source("https://defillama.com/recent")
    if page_source:
        soup = BeautifulSoup(page_source, "html.parser")
        table_container = soup.find("div", id="table-wrapper")
        if table_container:
            links = table_container.find_all("a", class_="text-sm font-medium text-[var(--link-text)] overflow-hidden whitespace-nowrap text-ellipsis hover:underline")
            for link in links:
                name = link.text
                href = "https://defillama.com" + link.get("href")
                projects.append({"name": name, "link": href})
    return projects if projects else None

async def get_defilama_project_details(url):
    social_links = []
    driver = await create_webdriver()
    
    try:
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: driver.get(url)
        )
        await asyncio.sleep(5)  # Non-blocking sleep

        social_block = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: driver.find_element(By.XPATH, "//*[@id='__next']/main/div/div[2]/div[2]/div[1]/div")
        )
        
        social_data = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: social_block.find_elements(By.TAG_NAME, "a")
        )
        
        for link in social_data:
            social_name = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: link.find_element(By.TAG_NAME, "span").get_property("textContent")
            )
            social_link = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: link.get_attribute("href")
            )
            if social_link:
                social_links.append({
                    "name": social_name,
                    "link": social_link
                })

        # get the forkend from info 
        try:
            forked_from  = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: driver.find_element(By.XPATH, "//*[@id='__next']/main/div/div[2]/div[2]/div[1]/p[3]")
            )
        except:
            print("No forked from info found")
            social_links.append({"forked_from": None})
            return social_links
        try:
            if forked_from:
                forked_from_text = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: forked_from.get_property("textContent")
                )
                if "Forked from" in forked_from_text:
                    forked_from = forked_from_text.split(":")[1]
                    forked_from = forked_from.strip()
                    social_links.append({"forked_from": forked_from})
                else:
                    social_links.append({"forked_from": None})
                    return social_links
                    
                forked_from = forked_from.strip()
                social_links.append({"forked_from": forked_from})
        except:
            print("No forked from info found")
            return social_links.append({"forked_from": None})
            
        return social_links
    except Exception as e:
        print(f"Error getting page source: {e}")
        return None
    finally:
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: (driver.close(), driver.quit())
        )
