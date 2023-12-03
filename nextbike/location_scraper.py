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

    # get html content of current page (post log in)
    page = driver.page_source

    # parse into beautiful soup object
    soup = BeautifulSoup(page, "html.parser")
    

    # scrape latitude and longitude    
    try:
        latitude_input = soup.find("input", id="parameters[lat]")
        #print("this is latitude_input:", latitude_input)
        latitude = latitude_input.get("value")
        print(latitude)
    except AttributeError:
        print("no lat")
        driver.back()
        return
    
    try:
        longitude_input = soup.find("input", id = "parameters[lng]")
        longitude = longitude_input.get("value")
        (print(longitude))
    except AttributeError:
        print("no long")
        driver.back()
        return

    # insert into table and return to previous page
    update_query = "UPDATE processed_stations SET latitude = ?, longitude = ? WHERE Place_name = ?"
    update_list = [latitude, longitude, station_name]
    cursor.execute(update_query, update_list)
    conn.commit()

    cursor.execute("SELECT * FROM processed_stations WHERE Place_name = ?", (station_name,))
    updated_row = cursor.fetchone()  
    conn.commit()
    print(updated_row)
    
    #does it need more time to update?
    driver.implicitly_wait(1)
    driver.back()

'''this is an unfinished piece of code to deal with the issue of search terms throwing multiple options. would be better with something like if page url has places/?action then check counter, is 0 take first one from classes and increase counter, but its only 5 so maybe i do by hand'''
def nav_scrape2(station_name):

    driver.implicitly_wait(0.5)
    location = driver.find_element(by=By.CLASS_NAME, value="place_name")
    location.click()
    nav_scrape(station_name)




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
cursor.execute("SELECT * FROM processed_stations WHERE  Place_type IN ('E-bike station', 'Standard place');")

# fetch all table data into iterable
rows = cursor.fetchall()

# initiate loop and skip first row (headers)
print("initiating loop")
first_row = True 
print("first row true")
station_name = ""
for row in rows:
    if first_row:
        first_row = False
        continue
    #call function that takes in place name and inserts lat and long into table
    station_name = (row[1])
    '''this bit really is not optimal. needs to be dealt with inside nav_scrape'''
    if station_name == "glasgow green":
        nav_scrape2(station_name)

    print(station_name)
    nav_scrape(station_name)
    print(row)    



