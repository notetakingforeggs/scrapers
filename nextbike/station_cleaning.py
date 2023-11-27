import csv
import sqlite3


# reading csv
with open("stations_raw.csv", "r") as csvfile:
    csvreader = csv.reader(csvfile, delimiter = '\t')
    header = next(csvreader)
     
    # connect to db
    conn = sqlite3.connect('stations.db')
    cursor = conn.cursor()

    # i want to take only place name, place number, place type
    selected_columns = [header[3], header[5], header[8]]
    cleaned_columns = [header.replace(" ", "_") for header in selected_columns]

    # create table
    create_table = f"CREATE TABLE IF NOT EXISTS processed_stations (id INTEGER PRIMARY KEY AUTOINCREMENT, {', '.join(cleaned_columns)}, latitude REAL, longitude REAL);"
    cursor.execute(create_table)

    # create table insert string
    table_insert = f"INSERT INTO processed_stations VALUES (NULL, {('?, ') * (len(cleaned_columns))}NULL, NULL);"
    
            
    # select for only rows that are not solo bikes and input into table
    for row in csvreader:
        if "bike" in row[3].lower() or not row[5]: #contains string bike in lower?
            continue            
        wanted_data = [row[3], row[5], row[8]]
        cursor.execute(table_insert, wanted_data)
        
    
conn.commit()
            



    # once i have this table, i want to make an automation to go and collect longitude and lattitude and add it to the table


