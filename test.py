import streamlit as st

no_of_locations = int(st.text_input("Give how many locations you want: "))
industry_list = ['a', 'b', 'c']
l = []

for _ in range(no_of_locations):
    location_data = []
    row = st.columns(3)
    
    for i, industry in enumerate(industry_list):
        value = row[i].number_input(f"{industry} - Location {_ + 1}")
        location_data.append(value)
    
    l.append(location_data)

# Print the final list
st.write("Location Data List:", l)
