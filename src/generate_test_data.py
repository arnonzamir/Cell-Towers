#for a given lat and lon this script returns a csv file with subset of towers in 20km radius and a csv file with the bearings to each tower in 5km radius

import csv
from DataPoint import DataPoint
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import folium
import webbrowser
import os
import math
from pyproj import Proj, transform
from geo_calc import get_towers_within_radius, calculate_bearing
import argparse

#get lat and long from command line
parser = argparse.ArgumentParser()

parser.add_argument('--p', type=str, required=True, help='point of interest lat,lon. eg: --p 32.1234,34.1234')
args = parser.parse_args()
point_of_interest_lat, point_of_interest_lon = args.p.split(',')
point_of_interest_lat = float(point_of_interest_lat)
point_of_interest_lon = float(point_of_interest_lon)


filename = 'F:\code\Cell Towers\data\israel_lat_long.csv'
english_columns = [
    "ID", "provider", "side_id", "city", "address","muni","jurid",
    "X_ITM", "Y_ITM", "site_type", "cert_date", "oper_date",  
    "last_review_date", "cert_radiation", "max_rad", "max_rad_rel", "max_rad_description", "setup_file", "oper_file", "network_type",
    "longitude",  "latitude"
]

df = pd.read_csv(filename, header=None, names=english_columns)


print(f'found {len(df)} data points')
#remove duplicates
df.drop_duplicates(subset=['latitude', 'longitude'], inplace=True)
print(f'found {len(df)} unique data points')
  
df_radius_km = 8
test_radium_km = 5
#generate a test id from timestamp

test_id = str(int(pd.Timestamp.now().timestamp()))

training_group = get_towers_within_radius(df, point_of_interest_lat, point_of_interest_lon, df_radius_km)
print (f'found {len(training_group)} towers within {df_radius_km} km of {point_of_interest_lat}, {point_of_interest_lon}')
#save to csv
training_group.to_csv(f'df_subset_{test_id}.csv', index=False, header=False)

# Get towers within the specified radius
towers_within_radius = get_towers_within_radius(df, point_of_interest_lat, point_of_interest_lon, test_radium_km)
print (f'found {len(towers_within_radius)} towers within {test_radium_km} km of {point_of_interest_lat}, {point_of_interest_lon}')

#sort by max radiation level (higher first)
towers_within_radius.sort_values(by=['max_rad'], inplace=True, ascending=False)
#take at most 10 towers
towers_within_radius = towers_within_radius.head(10)

# Calculate the bearing to each tower within the radius
towers_within_radius['bearing'] = towers_within_radius.apply(
    lambda row: calculate_bearing(
        point_of_interest_lat, 
        point_of_interest_lon, 
        row['latitude'], 
        row['longitude']
    ), 
    axis=1
)

bearings = towers_within_radius['bearing'].values

#save to csv
with open(f'test_bearings_{test_id}.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(bearings)

print(f'towers saved to df_subset_{test_id}.csv')
print(f'bearings saved to test_bearings_{test_id}.csv')

# Create a map object, starting with mean coordinates for centering the map
map_center = [df['latitude'].mean(), df['longitude'].mean()]
mymap = folium.Map(location=map_center, zoom_start=8)
folium.Circle(
    location=[point_of_interest_lat, point_of_interest_lon],
    radius=test_radium_km*1000,
    color='crimson',
    fill=False,
).add_to(mymap)

folium.Circle(
    location=[point_of_interest_lat, point_of_interest_lon],
    radius=df_radius_km*1000,
    color='blue',
    fill=False,
).add_to(mymap)


# Add a marker for each data point
for index, row in towers_within_radius.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"{row['network_type']}: {row['latitude']}, {row['longitude']}, {row['provider']}"
    ).add_to(mymap)

# add markers for all the towers in the training group
for index, row in training_group.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=2,
        color='blue',
        fill=True
    ).add_to(mymap)

#draw a line from the point of interest to each tower
for index, row in towers_within_radius.iterrows():
    folium.PolyLine(
        locations=[(point_of_interest_lat, point_of_interest_lon), (row['latitude'], row['longitude'])],
        color='red',
        weight=2
    ).add_to(mymap)

mymap.show_in_browser()