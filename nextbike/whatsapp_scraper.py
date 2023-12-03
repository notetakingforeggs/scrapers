# import selenium  
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.common.exceptions import NoSuchElementException

driver = webdriver.Chrome()
# time imports
from dateutil.parser import parse
import time

# imports for beautiful soup
import requests
from bs4 import BeautifulSoup 

# import for db
import sqlite3

# connecting db
conn = sqlite3.connect("stations.db")
cursor = conn.cursor()

'''beginning automation'''

# navigate to web page
driver.get("https://web.whatsapp.com/")

# give time to scan QR
driver.implicitly_wait(5)
time.sleep(15) # replace this with explicit wait?

# find appropriate groupchat on page and click
station_checks = driver.find_element(by = By.XPATH, value = '//span[text() = "station checks"]')

# TODO I put a 3s sleep wait here, it was sometimes clicking and then it goes back to loading screen. should find more elegant way to do this.
time.sleep(3)
station_checks.click()


# scrolling up in whatsap chat
loop = False
while loop == False:
    try:
        today = driver.find_element(by=By.XPATH, value ='//span[text() = "THURSDAY"]')
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
 
# TODO then put it all on a web app and build a pretty front page