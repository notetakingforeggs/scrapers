
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
    m.get_root().width = "800px"
    m.get_root().height = "600px"
    iframe = m.get_root()._repr_html_()    

    # return the map template with the map (g last updated declared in link route)
    if hasattr(g, 'last_updated'):
        print(g.last_updated)
        return render_template("map_template.html", iframe=iframe, last_updated=g.last_updated)
    print("!hasattr")
    return render_template("map_template.html", iframe=iframe, last_updated="unknown")

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
                # will this stop the thread?
                print("probably logged in if still no QR - returning map")
                g.last_updated = f"{(datetime.now().date())}, {(datetime.now().time())}"
                print(g.last_updated)
                return redirect("/map")
        #return qr for scanning    
        print("returning scanme.html")
        return render_template("scanme.html")
    else:
        #here put a thing being like - already logged in
        print("QR exists already")
        whatsapp_scrape()
        g.last_updated = f"{(datetime.now().date())}"
        return redirect("/map")
    #this should update last checked only when log in has already occurred. should be fine
       

    




''' 
driver screenshots qr which is saved. 

after lunch: make browser headless. persistent log in from whatsapp. hide update button if not logged in? or at least give error page, upload to pyany'''