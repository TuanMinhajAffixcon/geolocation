import pandas as pd
import streamlit as st
import geohash2
from math import radians, sin, cos, sqrt, atan2
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np
import folium
from streamlit_folium import folium_static
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

st.title("Radius Search with WorkGeoHash and HomeGeoHash")

# Function to decode geohash into latitude and longitude
def decode_geohash(geohash):
    if pd.notna(geohash):
        try:
            latitude, longitude = geohash2.decode(geohash)
            return pd.Series({'Home_latitude': latitude, 'Home_longitude': longitude})
        except ValueError:
            # Handle invalid geohashes, you can modify this part based on your requirements
            return pd.Series({'Home_latitude': None, 'Home_longitude': None})
        except TypeError:
            # Handle the case where geohash2.decode returns a single tuple
            return pd.Series({'Home_latitude': geohash[0], 'Home_longitude': geohash[1]})
    else:
        # Handle null values
        return pd.Series({'Home_latitude': None, 'Home_longitude': None})
    
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
start_date = pd.Timestamp('2023-12-01')
end_date = pd.Timestamp('2023-12-31')

# Allow user to pick start and end dates
selected_start_date = st.sidebar.date_input("Select Start Date", start_date)
selected_end_date = st.sidebar.date_input("Select End Date", end_date)

# Convert date inputs to datetime objects
selected_start_date = pd.to_datetime(selected_start_date)
selected_end_date = pd.to_datetime(selected_end_date)

dist = st.radio("Select Distance Unit", ["Kilometers","Meters"])

df = pd.read_csv('10000_mevement.csv', sep=",").dropna(subset=['latitude', 'longitude'])
# server = os.getenv('SERVER')
# database = os.getenv('DATABASE')
# table_name = os.getenv('TABLE_NAME')


# connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database}'
# connection = pyodbc.connect(connection_string)
# sql_query = f'SELECT maid,datetimestamp,latitude,longitude,workgeohash,homegeohash9 FROM {table_name}'
# df = pd.read_sql(sql_query, connection)
# df=df.dropna(subset=['latitude', 'longitude'])
df['datetimestamp'] = pd.to_datetime(df['datetimestamp'])

df[['Home_latitude', 'Home_longitude']] = df['homegeohash9'].apply(decode_geohash)
df[['Work_latitude', 'Work_longitude']] = df['workgeohash'].apply(decode_geohash)

df = df[(df['datetimestamp'] >= selected_start_date) & (df['datetimestamp'] <= selected_end_date)]

st.text(f"Number of records within Date Range: {len(df)}")

# User input for specific locations in Australia
user_input_lat = st.sidebar.text_input("Enter a latitude:", value="-33.864201")
user_input_lon = st.sidebar.text_input("Enter a longitude :", value="151.21644")

if dist == 'Kilometers':
    radius_input = st.slider("Select radius (in kilometers):", min_value=1, max_value=100, value=10)

elif dist == 'Meters':
    radius_input = st.slider("Select radius (in Meters):", min_value=1, max_value=1000, value=10)
    radius_input=radius_input/1000

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
    
    filtered_df['Distance_To_Home (Km)'] = filtered_df.apply(lambda row:
        haversine(user_lat, user_lon, float(row['Home_latitude']), float(row['Home_longitude']))
        if pd.notna(row['Home_latitude']) and pd.notna(row['Home_longitude']) else None, axis=1)
    filtered_df['Distance_To_WorkPlace (Km)'] = filtered_df.apply(lambda row:
        haversine(user_lat, user_lon, float(row['Work_latitude']), float(row['Work_longitude']))
        if pd.notna(row['Work_latitude']) and pd.notna(row['Work_longitude']) else None, axis=1)
    
    filtered_df_home_backup=filtered_df.copy()
    filtered_df=filtered_df[['longitude','latitude','Distance_To_Home (Km)','Distance_To_WorkPlace (Km)']]
    filtered_df=filtered_df.sort_values('Distance_To_Home (Km)')


    with st.expander("View Filtered Data:"):
        st.write(filtered_df)

    folium_static(m)

    selected_distance = st.radio("Select Distance", ["Home-Distance", "Work-Distance"])

    def selection_distance(ColumnName,X_title,color,title):
        fig = px.histogram(filtered_df, x=filtered_df[ColumnName], nbins=int(filtered_df[ColumnName].max()-filtered_df[ColumnName].min())//3)
        fig.update_traces(marker_color=color, opacity=0.7)

        fig.update_layout({
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
            'xaxis': {'showgrid': False,'title': X_title},
            'yaxis': {'showgrid': False,'title': 'Total Count'},
        })

        st.write(title)
        st.plotly_chart(fig)

    if selected_distance=='Home-Distance':
        selection_distance('Distance_To_Home (Km)','Distance To Home (Km)','yellow',"Histogram of Home Distance")
    else:
        selection_distance('Distance_To_WorkPlace (Km)','Distance To Work (Km)','orange',"Histogram of Work Distance")


    filtered_df_home = filtered_df_home_backup[filtered_df_home_backup.apply(lambda row:
        (pd.notna(row['Home_latitude']) and pd.notna(row['Home_longitude'])) and
        haversine(user_lat, user_lon, float(row['Home_latitude']), float(row['Home_longitude'])) <= radius_input, axis=1)
    ]
    filtered_df_work = filtered_df_home_backup[filtered_df_home_backup.apply(lambda row:
        (pd.notna(row['Work_latitude']) and pd.notna(row['Work_longitude'])) and
        haversine(user_lat, user_lon, float(row['Work_latitude']), float(row['Work_longitude'])) <= radius_input, axis=1)
    ]

    st.text(f"Total Home counts inside the Radius: {len(filtered_df_home)}")
    st.text(f"Total WorkPlace counts inside the Radius: {len(filtered_df_work)}")


else:
    st.warning("Please enter both latitude and longitude values.")


    


