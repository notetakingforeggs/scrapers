# %%
import folium
from folium import plugins
from IPython.display import display, HTML

import sqlite3

import os

conn = sqlite3.connect("stations.db")
cursor = conn.cursor()

print("something")

# Create a map centered at a specific location
m = folium.Map(location=[55.8591, -4.2581], zoom_start=12)

# create table in code to iterate through


# TODO insert new columns of last checked, and have it filled by whatsapp scraper
# TODO have current date minus date last checked to get days unchecked
# temp slshn just do green = 0 to 1 days, orange 1 - 3 days red > 3 days. might be better tbh

stations = cursor.execute("SELECT * FROM processed_stations")
justone = True
for row in stations:
    if not row[4]:
        continue
    lat = row[4]
    lng = row[5]    
    last_checked = row[6]
    days_unchecked = row[7]

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

    if row[3] == "E-bike station":
        station_icon = folium.Icon(icon="asterisk", color = f"{colour}")
    else:
        station_icon = folium.Icon(icon="flash",color = f"{colour}")

 
    folium.Marker(
        location=[lat, lng],
        tooltip="click4deets",
        popup=f"Station:{row[1]}, last checked:{last_checked}",
        icon=station_icon,
    ).add_to(m) 
   
        
     

   


# Save the map to an HTML file
#m.save("map.html")



# %%