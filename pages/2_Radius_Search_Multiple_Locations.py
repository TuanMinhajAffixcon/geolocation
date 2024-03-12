import streamlit as st
import pandas as pd
from math import radians, sin, cos, sqrt, atan2

st.title("Radius Search with Multiple Locations")

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

selected_distance = st.radio("Select Radius Type", ["Fixed Radius", "Varying Radius"])

df = pd.read_csv('sample_Data_csv.csv', sep="|").dropna(subset=['latitude', 'longitude'])

# # Allow user to input multiple latitude and longitude locations
# locations = st.text_area("Enter multiple latitude and longitude coordinates (one pair per line):", value="-33.864201,151.21644\n-34.052235,118.243683")

# # Convert user input to list of tuples
# user_coordinates = [tuple(map(float, location.split(','))) for location in locations.split('\n') if location]

no_of_locations = st.text_input("Give how many locations you want: ")


# st.write(user_coordinates)


# if user_coordinates:
#     count_within_radius = {}
#     filtered_coordinates = {}
dist = st.radio("Select Distance Unit", ["Kilometers","Meters"])

if  no_of_locations:
    no_of_locations = int(no_of_locations)

    if selected_distance=="Fixed Radius":
        count_within_radius = {}
        filtered_coordinates = {}
        industry_list = ['latitude', 'longitude']
        user_coordinates = []

        for _ in range(no_of_locations):
            location_data = []
            row = st.columns(2)
            
            for i, industry in enumerate(industry_list):
                value = row[i].number_input(f"{industry} - Location {_ + 1}", format="%.6f")
                location_data.append(value)
            
            user_coordinates.append(location_data)
        if len(user_coordinates[0]) ==2:
            for user_lat, user_lon in user_coordinates:
                count_within_radius[(user_lat, user_lon)] = 0
                filtered_coordinates[(user_lat, user_lon)] = []
            if dist == 'Kilometers':
                radius_input = st.slider("Select radius (in kilometers):", min_value=1, max_value=100, value=10)

            elif dist == 'Meters':
                radius_input = st.slider("Select radius (in Meters):", min_value=1, max_value=1000, value=10)
                radius_input=radius_input/1000

            for index, row in df.iterrows():
                for user_lat, user_lon in user_coordinates:
                    distance = haversine(user_lat, user_lon, row['latitude'], row['longitude'])
                    if distance <= radius_input:
                        count_within_radius[(user_lat, user_lon)] += 1
                        filtered_coordinates[(user_lat, user_lon)].append((row['latitude'], row['longitude']))
        else:
            st.warning("Please Enter Only Longitude and Latitude Sequentially")

    else:
        count_within_radius = {}
        filtered_coordinates = {}
        industry_list = ['latitude', 'longitude', 'Radius']
        user_coordinates = []

        for _ in range(no_of_locations):
            location_data = []
            row = st.columns(3)
            
            for i, industry in enumerate(industry_list):
                value = row[i].number_input(f"{industry} - Location {_ + 1}", format="%.6f")
                location_data.append(value)
            
            user_coordinates.append(location_data)
        if len(user_coordinates[0]) ==3:
            for user_lat, user_lon, radius_input in user_coordinates:
                count_within_radius[(user_lat, user_lon)] = 0
                filtered_coordinates[(user_lat, user_lon)] = []
            for index, row in df.iterrows():
                for user_lat, user_lon, radius in user_coordinates:
                    distance = haversine(user_lat, user_lon, row['latitude'], row['longitude'])

                    if dist == 'Meters':
                        radius= radius/1000

                    if distance <= radius:
                        count_within_radius[(user_lat, user_lon)] += 1
                        filtered_coordinates[(user_lat, user_lon)].append((row['latitude'], row['longitude']))
        else:
            st.warning("Please Enter Only Longitude and Latitude and Radius Sequentially")

    count_df = pd.DataFrame(list(count_within_radius.items()), columns=['coordinates', 'count'])

    # Display the count DataFrame
    st.write("Count within radius for each location:")
    st.write(count_df)

else:
    st.warning("Please Enter No of Locations")
    # for user_lat, user_lon in user_coordinates:
    #     count_within_radius[(user_lat, user_lon)] = 0
    #     filtered_coordinates[(user_lat, user_lon)] = []
        

    # for index, row in df.iterrows():
    #     for user_lat, user_lon in user_coordinates:
    #         distance = haversine(user_lat, user_lon, row['latitude'], row['longitude'])
    #         if distance <= radius_input:
    #             count_within_radius[(user_lat, user_lon)] += 1
    #             filtered_coordinates[(user_lat, user_lon)].append((row['latitude'], row['longitude']))
    
    # for index, row in df.iterrows():
    #     for user_lat, user_lon,radius in user_coordinates:
    #         distance = haversine(user_lat, user_lon, row['latitude'], row['longitude'])
    #         if distance <= radius:
    #             count_within_radius[(user_lat, user_lon)] += 1
    #             filtered_coordinates[(user_lat, user_lon)].append((row['latitude'], row['longitude']))

    # count_df = pd.DataFrame(list(count_within_radius.items()), columns=['coordinates', 'lon']).assign(count=list(count_within_radius.values()))
    # count_df.drop('lon',axis=1,inplace=True)
    # # Display the count DataFrame
    # st.write("Count within radius for each location:")
    # st.write(count_df)









    # st.write(f"Count within radius for each location:")
    # for (user_lat, user_lon), count in count_within_radius.items():
    #     st.write(f"({user_lat}, {user_lon}): {count}")

    # st.write(f"Filtered coordinates for each location:")
    # for (user_lat, user_lon), coordinates in filtered_coordinates.items():
    #     st.write(f"({user_lat}, {user_lon}): {coordinates}")
