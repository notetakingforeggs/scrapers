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
station_checks.click()



# TODO scroll up to part where it says today? (assuming initiated run in the morning and on repeat every n hours. no point scraping 2 days at a time?)
''' so the rows maintain the same xpath but the iner html content changes'''
loop = False
while loop == False:
    try:
        today = driver.find_element(by=By.XPATH, value ='//span[text() = "TODAY"]')
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

#print(tab_index.prettify())
'''
content = tab_index.find_all('span', class_= None)
for span in content:
    print(span.text.strip())'''

date_content = tab_index.find_all('div', class_='copyable-text')
for div in date_content:
        contains_date = div['data-pre-plain-text']

        parsed_date = parse(contains_date,fuzzy=True)
        date = str(parsed_date.date())
        print(f"the date is: {date}")
       
        
        spans = div.find_all('span', class_= None)
        for span in spans:
            # TODO this needs to be fixed so it searches string inside span for and returns the place number - wont work if there is more text than just that
            try:
                place_number = int(span.text.strip())

            except ValueError:
                continue
            print("station code is:", place_number)
            print("-----------------")

        cursor.execute("UPDATE processed_stations SET last_checked = ? WHERE Place_number = ?", (date, place_number))
        conn.commit()
        print('tried to add')
# TODO also insert a columns of date since last check which goes thru each station and subtracts the date since last checkd from the current date to get a nubmer of days.
'''        
a-could scrape date and time from each message to add to the table

b-could clear whatsapp chat history at the end of each cycle, so that every scanned message could only be scanned on the day it was posted

a would be more coding in the scrape, and more date into the table.
b would involve a further selenium automation at the end of each cycle which tends to be kinda slow, but would also keep the chat clean
but maybe someone wants that chat

a feels harder, but also feels cleaner.
'''


# TODO find in this soup everytime a station code is mentioned, insert the date into the date column of the table IF the current cell value isnt the same date?
'''maybe in here there is some value in optimising search strategy at some point?'''
# TODO loop through processed stations to populate a "days since last check" column

# TODO Feed in last checked status to icons in folium

# TODO then put it all on a web app and build a pretty front page