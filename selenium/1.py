# imports for selenium 
from selenium import webdriver
from selenium.webdriver.common.by import By
driver = webdriver.Chrome()

# imports for beautiful soup
import requests
from bs4 import BeautifulSoup

# import for db
import sqlite3

conn = sqlite3.connect("tutors.db")
cursor = conn.cursor()


# navigate to web page
driver.get("https://www.tutorhunt.com/")

# request browser info (here just title)
title = driver.title


# establish waiting strategy
driver.implicitly_wait(0.5)

list_of_subjects = ["chemistry", "biology", "english", "physics"]
for current_subject in list_of_subjects:
    print("starting a page")
    # find items on page to interact with
    subject = driver.find_element(by=By.ID, value = "subject")
    buttons = driver.find_elements(by=By.TAG_NAME, value = "button")

    # take action on elements
    subject.clear()
    subject.send_keys(f"{current_subject}")
    buttons[0].click()

    # wait for page to load
    driver.implicitly_wait(0.5)

    # create table
    print(f"creating table: {current_subject}")
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {current_subject} (id INTEGER PRIMARY KEY, name TEXT, member_for INT, hours_taught INT, fee REAL, yearly_hours REAL GENERATED ALWAYS AS (hours_taught/member_for) STORED, yearly_pay REAL GENERATED ALWAYS AS (yearly_hours*fee) STORED);")  

    # set current url to that retrieved from driver
    current_URL = driver.current_url

    #URL = "https://www.tutorhunt.com/search-results.asp?amountlower=10&amounthiger=100&ratingval=1&chkteacher=0&chkdegree=0&chkdbs=0&sortby=rank&tuitiontype=online&subjectid=Maths&subject=Maths&level=all&postcode=&sourcepage=searchresults&searchsource=sr&filter=1&type=tutor&chkmale=1&chkfemale=1&chkinternational=0&searchtext=&onlineproximity=&onlinepostcode="
    page = requests.get(current_URL)

    # parse page into soup object
    soup = BeautifulSoup(page.content, "html.parser")

    # narrow down to tutor profile items within container
    results = soup.find(id="resultblockcontainer")


    # define tutor elements as everything of the class that contains tutor info
    tutor_elements = soup.find_all("div", class_="usercardmaincontentcontainer")


    # initiate looping through tutor elements
    for tutor_element in tutor_elements:

        # declaring variables so they are accessible outside of their inner loops
        name = None
        year_num = None 
        int_hours = None
        price = None

        # find name of tutor
        links = tutor_element.find_all("a") 
        for link in links:
            name = link.text.strip()
            #print(name)

        # find length of membership   
        member_fors = tutor_element.find_all("div", class_="usercard2metavalue", string=lambda text: "years" in text.lower())
        for member_for in member_fors:
            # iterate through string, check if each char is a digit and if yes cat it into year_num
            year_num = "" 
            for char in member_for.text.strip():
                if char.isdigit():
                    year_num += char
                else:
                    break
            #print("active member for: ", year_num, "years")
        
        # find hours taught

        # isolate by using specific icon associated with div containing hours
        check_icons = tutor_element.find_all("use", {"xlink:href": "/images/sprite2.svg#checkcircle"})
        for check_icon in check_icons:
            target_div = check_icon.find_parent("div")
            inner_html = str(target_div)
            hours = "" 
            for char in target_div.text.strip():
                if char.isdigit():
                    hours+=char
                else:
                    break
            int_hours = int(hours)
            #print("has worked a total of: ", int_hours, "hours")


        # find price per hour
        prices = tutor_element.find_all("div", class_="usercard2ratevalue")
        for price in prices:

            price_parts = price.text.replace("£", "").split(" - ")
            if len(price_parts) == 1:
                price = float(price_parts[0])
                #print("charges on average:", price)

            elif len(price_parts) == 2:
                lower = float(price_parts[0])
                higher = float(price_parts[1])
                price = (lower+higher)/2
                #print("charges on average:", price)


        # calculate total amounts earnt and income per x
        print(f"Inserting data into table: {current_subject}")
        cursor.execute(f"INSERT INTO {current_subject} (name, member_for, hours_taught, fee) VALUES (?, ?, ?, ?)", (name, year_num, int_hours, price,))
        conn.commit()

    driver.back()
    driver.implicitly_wait(0.5)
    


driver.quit()
