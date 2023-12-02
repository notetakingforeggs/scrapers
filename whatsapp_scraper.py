# import selenium  
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.common.exceptions import NoSuchElementException

driver = webdriver.Chrome()

from dateutil.parser import parse
import time

# imports for beautiful soup
import requests
from bs4 import BeautifulSoup 

# import for db
import sqlite3

conn = sqlite3.connect("stations.db")
cursor = conn.cursor()


# navigate to web page
driver.get("https://web.whatsapp.com/")

# give time to scan QR
driver.implicitly_wait(5)
time.sleep(15) # replace this with explicit wait?

# find appropriate groupchat on page and click
#tats = driver.find_element(by=By.XPATH, value='//span[text() = "Tats"]')
#tats.click()
station_checks = driver.find_element(by = By.XPATH, value = '//span[text() = "station checks"]')
# TODO need more wait here, sometimes clicking and then it goes back to loading screen. click too early?
station_checks.click()



# TODO scroll up to part where it says today? (assuming initiated run in the morning and on repeat every n hours. no point scraping 2 days at a time?)
''' so the rows maintain the same xpath but the iner html content changes'''
loop = False
while loop == False:
    try:
        today = driver.find_element(by=By.XPATH, value ='//span[text() = "THURSDAY"]')
        print ("foound")
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

# make soup object out of page with stations on it from where it says today/yesterday
page = driver.page_source
soup = BeautifulSoup(page, "html.parser")

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
            # TODO this needs to be fixed so it searches string inside span for and returns the place number - wont work if there is more text than just that
            try:
                place_number = (span.text.strip())
                
                int(place_number)
            except ValueError:
                print("value error")
                continue
            print("station code is:", place_number)
            

        # update db
        cursor.execute("UPDATE processed_stations SET last_checked = ? WHERE Place_number = ?", (date, place_number,))
        conn.commit()
        cursor.execute("UPDATE processed_stations SET days_since = CAST(julianday('now') - julianday(last_checked) AS INTEGER);")        
        conn.commit()
        print('tried to add')







# TODO find in this soup everytime a station code is mentioned, insert the date into the date column of the table IF the current cell value isnt the same date?
'''maybe in here there is some value in optimising search strategy at some point?'''



# TODO then put it all on a web app and build a pretty front page