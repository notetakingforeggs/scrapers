import requests
from bs4 import BeautifulSoup
import sqlite3
conn = sqlite3.connect("tutors.db")
cursor = conn.cursor()


# get webpage
URL = "https://www.tutorhunt.com/search-results.asp?amountlower=10&amounthiger=100&ratingval=1&chkteacher=0&chkdegree=0&chkdbs=0&sortby=rank&tuitiontype=online&subjectid=Chemistry&subject=Chemistry&level=all&postcode=&sourcepage=searchresults&searchsource=sr&filter=1&type=tutor&chkmale=1&chkfemale=1&chkinternational=0&searchtext=&onlineproximity=&onlinepostcode="
page = requests.get(URL)

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
        print(name)

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
        print("active member for: ", year_num, "years")
    
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
        print("has worked a total of: ", int_hours, "hours")


    # find price per hour
    prices = tutor_element.find_all("div", class_="usercard2ratevalue")
    for price in prices:

        price_parts = price.text.replace("£", "").split(" - ")
        if len(price_parts) == 1:
            price = float(price_parts[0])
            print("charges on average:", price)

        elif len(price_parts) == 2:
            lower = float(price_parts[0])
            higher = float(price_parts[1])
            price = (lower+higher)/2
            print("charges on average:", price)


    # calculate total amounts earnt and income per x
    cursor.execute("INSERT INTO tutors (name, member_for, hours_taught, fee) VALUES (?, ?, ?, ?)", (name, year_num, int_hours, price,))
    conn.commit()
    
    print("----")

cursor.execute("SELECT * FROM tutors")
rows = cursor.fetchall()
for row in rows:
    print(row)
  

   
