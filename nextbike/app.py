
# flask imports
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from map import map
from whatsapp_scraper import whatsapp_scrape
import sqlite3
import os


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
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

    # return the map template with the map 
    return render_template("map_template.html", iframe=iframe)

# update route
@app.route("/update")
def update_db():
    
    # call whatsapp scrape function
    whatsapp_scrape()
    # redirect to map page 
    return redirect("/map") 




