
# flask imports
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session

# imports for map
import folium
from folium import plugins
from IPython.display import display, HTML
import sqlite3
import os

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# connect to stations database
import sqlite3
conn = sqlite3.connect("stations.db")
cursor = conn.cursor()


@app.route("/")
def index():
    print("tried to return index")
    return render_template("index.html")

@app.route("/map_display")
def map_display():
    return render_template("map_template.html")


@app.route("/map")
def map_make():
    conn = sqlite3.connect("stations.db")
    cursor = conn.cursor()

    # Create a map centered at a specific location (glasgow central)
    m = folium.Map(location=[55.8591, -4.2581], zoom_start=12)

    # create iterable from db
    stations = cursor.execute("SELECT * FROM processed_stations")

    # initiate loop
    justone = True
    for row in stations:

        # skip if no lat
        if not row[4]:
            continue

        # set latitude and longitude, last checked and days unchecked to columns from table
        lat = row[4]
        lng = row[5]    
        last_checked = row[6]
        days_unchecked = row[7]

        # create colours for icons depeneding on days unchecked
        try:
            if (days_unchecked == None):
                colour = "red"
            elif (days_unchecked < 2):
                colour = "green"
            elif (4 > days_unchecked > 1):
                colour = "orange"
            else:
                colour = "red"
            
        except TypeError:
            print("typeerrorboiiiii")
            continue

        # give different icons to normal / ebike stations
        if row[3] == "E-bike station":
            station_icon = folium.Icon(icon="asterisk", color = f"{colour}")
        else:
            station_icon = folium.Icon(icon="flash",color = f"{colour}")

        # create markers on map
        folium.Marker(
            location=[lat, lng],
            tooltip="click4deets",
            popup=f"Station:{row[1]}, last checked:{last_checked}",
            icon=station_icon,
        ).add_to(m) 

    # save the map as a html file         
    m.save("map.html")

    # get the root of the map and render into a html string
    m.get_root().width = "800px"
    m.get_root().height = "600px"
    iframe = m.get_root()._repr_html_()    

    # return the map template with the map 
    #return render_template("map.html")
    #return render_template("map_template.html", mop=html_map, othervar = "cheese")
    return render_template("map_template.html", iframe=iframe)
    




