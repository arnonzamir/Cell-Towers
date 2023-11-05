import csv
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import folium
import numpy as np
import math
from pyproj import Proj, transform
from geo_calc import get_towers_within_radius, calculate_bearing
from geopy.distance import geodesic
from sklearn.cluster import DBSCAN

english_columns = [
    "ID", "provider", "side_id", "city", "address","muni","jurid",
    "X_ITM", "Y_ITM", "site_type", "cert_date", "oper_date",  
    "last_review_date", "cert_radiation", "max_rad", "max_rad_rel", "max_rad_description", "setup_file", "oper_file", "network_type",
    "longitude",  "latitude"
]

test_csv_file = 'df_subset_1699025468.csv'
test_bearings_file = 'test_bearings_1699025468.csv'

#read the whole bearings file as a string 
with open(test_bearings_file, 'r') as f:
    str_bearings = f.read()

bearings = str_bearings.split(',')
bearings = [float(b) for b in bearings]

#load the test csv file to df
df = pd.read_csv(test_csv_file, header=None, names=english_columns)

print (f'found {df.shape[0]} towers in {test_csv_file}')
print (f'found {len(bearings)} bearings')

#get center point of df
center_lat = df['latitude'].mean()
center_lon = df['longitude'].mean()
distance = 8

def compute_endpoint(lat, lon, angle, distance=8):
    start = (lat, lon)
    endpoint = geodesic(kilometers=distance).destination(start, angle)
    return endpoint.latitude, endpoint.longitude

def line_intersection(line1, line2):
    """Return the intersection point of two lines, each defined by a pair of points."""
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        return None  # Lines don't intersect

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y

tower_headings = dict()
for i, row in df.iterrows():
    #add an empty list for each tower

    tower_headings[row["ID"]] = [[row['latitude'], row['longitude']]]

for j, row in df.iterrows():
    lat = row['latitude']
    lon = row['longitude']
    id = row['ID']
    for i in range(len(bearings)):
        bearing = bearings[i]
        ep_lat, ep_lon = compute_endpoint(lat, lon, bearing+180, distance)
        tower_headings[id].append([ep_lat, ep_lon])

#flatten the list to an array of lines 
lines = []
for id, headings in tower_headings.items():
    for i in range(len(headings)-1):
        if i == 0:
            continue
        lines.append([headings[0], headings[i]])


intersection_points = []
for i in range(len(lines)):
    for j in range(len(lines)):
        if i == j:
            continue
        intersection = line_intersection(lines[i], lines[j])
        if intersection is not None:
            intersection_points.append(intersection)

intersection_points = np.array(intersection_points)
print(intersection_points.shape)
print(f'found {len(intersection_points)} intersection points')

#draw on folium map
# Create a map
m = folium.Map(location=[center_lat, center_lon],  zoom_start=8)

# # Add points to the map
# for i, row in df.iterrows():
#     lat = row['latitude']
#     lon = row['longitude']
#     id = row['ID']
#     folium.CircleMarker(location=[lat, lon], radius=5, color='red', fill=True).add_to(m)

# #for each tower, draw all the lines 
# for id, headings in tower_headings.items():
#     for i in range(len(headings)-1):
#         if i == 0:
#             continue
#         folium.PolyLine(locations=[headings[0], headings[i]], color='yellow', stroke = True, weight = 1).add_to(m)

# for i in range(len(intersection_points)):
#     folium.CircleMarker(location=[intersection_points[i][0], intersection_points[i][1]], radius=1, stroke=True, weight=1, color='green', fill=True).add_to(m)

db = DBSCAN(eps=1, min_samples=5).fit(intersection_points)  # eps is the maximum distance between two samples for one to be considered in the neighborhood of the other. Adjust this value based on your data.
labels = db.labels_

answer_lat = 32.321555
answer_lon = 34.982414


# for i in range(len(bearings)):
#     bearing = bearings[i]
#     ep_lat, ep_lon = compute_endpoint(answer_lat, answer_lon, bearing, distance)
#     folium.PolyLine(locations=[[answer_lat, answer_lon], [ep_lat, ep_lon]], color='green').add_to(m)

folium.CircleMarker(location=[answer_lat, answer_lon], radius=20, color='green', fill=True).add_to(m)

m.show_in_browser()



