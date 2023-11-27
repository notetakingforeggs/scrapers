# import selenium  
from selenium import webdriver
from selenium.webdriver.common.by import By
driver = webdriver.Chrome()

# imports for beautiful soup
import requests
from bs4 import BeautifulSoup 

# import for db
import sqlite3


'''this is a function to navigate to the station page and scrape location data'''
def nav_scrape(station_name):

    # find items on page
    driver.implicitly_wait(0.5)
    location = driver.find_element(by=By.ID, value="parameters[search_term]")
    search_button = driver.find_element(by=By.ID, value = "places_get")

    # take action on elements
    location.clear()
    location.send_keys(f"{station_name}")
    search_button.click()
    driver.implicitly_wait(0.5)

    # get URL of current page
    current_url = driver.current_url

    # get content of current page
    page = requests.get(current_url)

    # parse into beautiful soup object
    soup = BeautifulSoup(page.content, "html.parser")

    # scrape latitude and longitude
    try:
        latitude_input = soup.find(id = "parameters[lat]")
        latitude = latitude_input.get("value")
    except AttributeError:
        print("no location")
        driver.back()
        return

    try:
        longitude_input = soup.find(id = "parameters[lng]]")
        longitude = latitude_input.get("value")
    except AttributeError:
        print("no location")
        driver.back()
        return

    # insert into table and return to previous page
    cursor.execute(f"INSERT INTO processed_stations WHERE name IS {station_name} (lattitude, longitude) VALUES (?, ?,)", latitude, longitude)
    print
    conn.commit()
    driver.back()





''' this is the start of the main code'''

conn = sqlite3.connect("stations.db")
cursor = conn.cursor()

# navigate to web page
driver.get("https://my.nextbike.net/office/places/")
driver.implicitly_wait(0.5)

# find items on page 
username = driver.find_element(by=By.ID, value ="parameters[username]")
password = driver.find_element(by=By.ID, value="parameters[password]")
button = driver.find_element(by=By.ID, value ="login_post")

# take action on elements
username.send_keys("jonahrussell")
password.send_keys("571416")
button.click()
driver.implicitly_wait(0.5)



#initiate loop through stations in table, so i can input station name into 

# select all from table
cursor.execute("SELECT * FROM processed_stations;")

# fetch all table data into iterable
rows = cursor.fetchall()

# initiate loop and skip first row (headers)
print("initiating loop")
first_row = True 
print("first row true")
for row in rows:
    if first_row:
        first_row = False
        continue
    #call function that takes in place name and inserts lat and long into table
    nav_scrape(row[1])    



