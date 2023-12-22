# import selenium  
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

# time imports
from dateutil.parser import parse
import time

# alterations to chromedriver to allow it to run headless, and thus on python anywhere
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
# this to solve issue of headless browser using old chrome or something?
chrome_options.add_argument("user-agent=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")

chrome_options.add_argument('--user-data-dir=./User_Data')
driver = webdriver.Chrome(options=chrome_options)

# imports for beautiful soup
import requests
from bs4 import BeautifulSoup 

# import for db
import sqlite3
''' not working, how can i use the same logged in webdriver? idk'''
def update():
    # connecting db
    conn = sqlite3.connect("stations.db")
    cursor = conn.cursor()

    '''beginning automation'''

    # navigate to web page
    print("IN THE SCRAPE FUNCTION NOW")
    driver.get("https://web.whatsapp.com/")   
    
    # find appropriate groupchat on page and click  
    #print("loading whatsapp web")
    #time.sleep(9)
    driver.save_screenshot("hasitloaded.png")
    element_locator = (By.XPATH, '//span[text() = "station checks"]')
    try:
        station_checks = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located(element_locator)
    )
    except TimeoutException:
        print("couldnt find stationchecks")
        driver.save_screenshot("thiswhereimat.png")
    # click on station checks chat.
    driver.save_screenshot("stationcheckspresent.png")
    station_checks.click()


    # scrolling up in whatsap chat
    loop = False
    counter = 0
    while loop == False and counter < 4:
        try:
            counter +=1
            today = driver.find_element(by=By.XPATH, value ='//span[text() = "YESTERDAY"]')
            print ("scrolling up complete")
            loop = True
        except NoSuchElementException:
            print("not found, scrolling up")
            iframe = driver.find_element(by=By.XPATH, value ='//div[@class = "n5hs2j7m oq31bsqd gx1rr48f qh5tioqs"]')
            scroll_origin = ScrollOrigin.from_element(iframe)
            ActionChains(driver)\
            .scroll_from_origin(scroll_origin, 0, -10000)\
            .perform()

    print(" try statement passed, scrolling done, initiating scrape")
    time.sleep(3)

    ''' beginning scrape '''
    # make soup object out of page with stations on it
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")

    #find the lowest container that holds all the information to scrape
    tab_index = soup.find('div', class_= 'n5hs2j7m oq31bsqd gx1rr48f qh5tioqs')

    # find the deepest div type containing both the date and the place number and iterate through them
    date_content = tab_index.find_all('div', class_='copyable-text')
    for div in date_content:
            
            # extract date
            contains_date = div['data-pre-plain-text']
            parsed_date = parse(contains_date,fuzzy=True)
            date = str(parsed_date.date())
            print(f"the date is: {date}")
        
            # extract place number
            place_number = None
            spans = div.find_all('span', class_= None)                
            for span in spans:            
                station_codes = cursor.execute('SELECT place_number FROM processed_stations')
                for station_code in station_codes:
                    if (station_code[0] in span.text.strip()):
                        print(station_code[0])
                        place_number = station_code[0]
                        int(place_number)
                    else:
                        continue
            print("station code is:", place_number)
                

            # update db to include the date last checked, and below to calculate the time since last checked. could combine to one line maybe?
            cursor.execute("UPDATE processed_stations SET last_checked = ? WHERE Place_number = ?", (date, place_number,))
            conn.commit()
            cursor.execute("UPDATE processed_stations SET days_since = CAST(julianday('now') - julianday(last_checked) AS INTEGER);")        
            conn.commit()
            print("station last checked updated")
    
    return