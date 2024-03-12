import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
from math import radians, sin, cos, sqrt, atan2
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np

# Set up Streamlit app
st.title("Radius Search with Selected Date Range")


# Function to calculate Haversine distance between two coordinates
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in kilometers

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Calculate differences
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Distance in kilometers
    distance = R * c
    return distance

# Function to generate points along the circumference of a circle
def generate_circle_points(center_lat, center_lon, radius, num_points=100):
    circle_points = []
    for i in range(num_points):
        angle = 2 * radians(i * (360 / num_points))
        lat = center_lat + (radius / 111.32) * sin(angle)
        lon = center_lon + (radius / (111.32 * cos(center_lat))) * cos(angle)
        circle_points.append((lat, lon))
    return circle_points
# Generate random datetime values
start_date = pd.Timestamp('2024-02-01')
end_date = pd.Timestamp('2024-02-29')

# Allow user to pick start and end dates
selected_start_date = st.sidebar.date_input("Select Start Date", start_date)
selected_end_date = st.sidebar.date_input("Select End Date", end_date)

# Convert date inputs to datetime objects
selected_start_date = pd.to_datetime(selected_start_date)
selected_end_date = pd.to_datetime(selected_end_date)

df = pd.read_csv('sample_Data_csv.csv', sep="|").dropna(subset=['latitude', 'longitude'])
time=pd.read_csv('random_datetime_values.csv')
time['datetime_values'] = pd.to_datetime(time['datetime_values'])
df=pd.concat([df,time],axis=1).dropna(subset=['latitude', 'longitude'])

df = df[(df['datetime_values'] >= selected_start_date) & (df['datetime_values'] <= selected_end_date)]

st.text(f"Number of records within Date Range: {len(df)}")

# User input for specific locations in Australia
user_input_lat = st.sidebar.text_input("Enter a latitude:", value="-33.864201")
user_input_lon = st.sidebar.text_input("Enter a longitude :", value="151.21644")
radius_input = st.slider("Select radius (in kilometers):", min_value=1, max_value=100, value=10)

# Process user input
if user_input_lat and user_input_lon:
    user_lat = float(user_input_lat)
    user_lon = float(user_input_lon)

    # Create a folium map centered on the user-specified location
    m = folium.Map(location=[user_lat, user_lon], zoom_start=10)

    # Plot sample data as blue points
    for lat, lon in zip(df['latitude'], df['longitude']):
        color = 'blue'
        folium.CircleMarker(location=[lat, lon], radius=2, color=color, fill=True, fill_color=color,
                            fill_opacity=1).add_to(m)

    # Highlight the user-specified location as a red point
    folium.CircleMarker(location=[user_lat, user_lon], radius=4, color='red', fill=True, fill_color='red',
                        fill_opacity=1).add_to(m)

    # Perform radius search and count points within the specified radius
    count_within_radius = 0
    for index, row in df.iterrows():
        distance = haversine(user_lat, user_lon, row['latitude'], row['longitude'])
        if distance <= radius_input:
            count_within_radius += 1

    # Display the count
    st.text(f"Number of points within {radius_input} km radius: {count_within_radius}")

    # Draw a circle around the user-specified location
    circle_points = generate_circle_points(user_lat, user_lon, radius_input)
    folium.PolyLine(circle_points, color='green', weight=2.5, opacity=1).add_to(m)
    filtered_df = df[df.apply(lambda row: haversine(user_lat, user_lon, row['latitude'], row['longitude']) <= radius_input, axis=1)]
    # st.write(filtered_df)

    folium_static(m)

else:
    st.warning("Please enter both latitude and longitude values.")

