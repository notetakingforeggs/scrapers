import folium
from IPython.display import display, HTML

m = folium.Map(location=(55.8591, -4.2581), zoom_start=13)

m.save("map.html")

display(HTML('<a href="map.html" target="_blank">Open Map</a>'))