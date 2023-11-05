import math 

def haversine(lat1, lon1, lat2, lon2):
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return km

def get_towers_within_radius(df, lat, lon, radius_km):
    towers_within_radius = df[df.apply(lambda row: haversine(lat, lon, row['latitude'], row['longitude']) <= radius_km, axis=1)]
    return towers_within_radius

def calculate_bearing(lat1, lon1, lat2, lon2):
    # Convert from degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(dlon))

    initial_bearing = math.atan2(x, y)
    
    # Convert from radians to degrees
    initial_bearing = math.degrees(initial_bearing)
    
    # Normalize the bearing
    compass_bearing = (initial_bearing + 360) % 360
    
    return compass_bearing

