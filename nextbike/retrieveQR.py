# import selenium  
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.common.exceptions import NoSuchElementException

# time imports
from dateutil.parser import parse
import time

import os


chrome_options = webdriver.ChromeOptions()

chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
# this to solve issue of headless browser using old chrome or something?
chrome_options.add_argument("user-agent=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
chrome_options.add_argument('--user-data-dir=./User_Data')
driver = webdriver.Chrome(options=chrome_options)


def retrieve_qr():   

    '''beginning automation'''

    # navigate to web page
    print("IN THE QR RETRIEVAL FUNCTION NOW")
    #driver.get("https://web.whatsapp.com/")

    # active wait for and locate QR code
    time.sleep(1)
    driver.save_screenshot("qrorloggedin.png")
    element_locator = (By.XPATH, '/html/body/div[1]/div/div[2]/div[3]/div[1]/div/div/div[2]/div/canvas')
    QR = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located(element_locator)
    )
    print("QR should be visible, screenshot now")

    # screenshot QR   
    QR.screenshot('static/QR.png')

    # wait for XPATH of something past the QR
    try:
        next_element_locator = (By.XPATH, '//*[@id="app"]/div/div[2]/div[3]/header/div[2]/div/span/div[4]/div/span')
        newchat = WebDriverWait(driver, 100).until(
            EC.visibility_of_element_located(next_element_locator)
        )
       
    except TimeoutError:
        print("couldnt find element post log in")
        #driver.close()

    # save screenshot to check login
    driver.save_screenshot("passedlogin.png")

    # Delete QR png
    #os.remove("static/QR.png")
    #print("QR.png deleted")

    # close driver
    #driver.close()
    #print("driver has quit")
    print("end of retrieval function")
    