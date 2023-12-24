
# flask imports
from flask import Flask, flash, redirect, render_template, request, session, g 
from flask_session import Session
from map import map
from whatsapp_scraper import whatsapp_scrape
from update import update
import sqlite3
import os
from retrieveQR import retrieve_qr
import time
from datetime import datetime
from threading import Thread
import shutil

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['STATIC_FOLDER'] = 'static'
Session(app) 

# connect to stations database
conn = sqlite3.connect("stations.db")
cursor = conn.cursor()




# homepage/index
@app.route("/")
def index():
    print("tried to return index")
    return render_template("index.html")

# map route
@app.route("/map")
def map_make():

    # call map function to generate map
    m = map()     
    
    # get the root of the map and render into a html string
    m.get_root().width = "100%"
    m.get_root().height = "500px"
    iframe = m.get_root()._repr_html_()    

    # return the map template with the map            
    return render_template("map_template.html", iframe=iframe)
    

# link device/update unified route
@app.route("/link")
def link():
    if not os.path.exists("static/QR.png"):
        # Initiate QR retrieval as background process
        thread = Thread(target=whatsapp_scrape)
        thread.start()

    
        # wait for QR to render template
        print("also checking for QR")
        counter = 0
        while not os.path.exists("static/QR.png"):
            print("no QR yet")
            time.sleep(5)
            counter +=1
            if counter >= 5:                
                print("probably logged in if still no QR - returning map")                
                return redirect("/map")
        #return qr for scanning    
        print("returning scanme.html")
        #put a thing here saying you have x amount of time to scan. maybe a countdown?
        return render_template("scanme.html")
    else:
        #here put a thing being like - already logged in
        print("QR exists already")
        try:
            whatsapp_scrape()        
            return redirect("/map")
        except UnboundLocalError:
            print("update attempted unlinked")
            os.remove("static/QR.png")
            shutil.rmtree("User_Data") 
            print("removed User Data and QR.png. try link again")
            #here make a new page saying, plase link again
            return redirect('/link')
        
        #when home make new page as above. check and test

    
''' also would be good to make a de-link button maybe? which does the same as above but onclick'''
       