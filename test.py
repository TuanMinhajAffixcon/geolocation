import streamlit as st
import pandas as pd
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

server = os.getenv('SERVER')
database = os.getenv('DATABASE')
table_name = os.getenv('TABLE_NAME')


connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database}'
connection = pyodbc.connect(connection_string)

# # SQL query
sql_query = f'SELECT maid,datetimestamp,latitude,longitude,workgeohash,homegeohash9 FROM {table_name}'

# Fetch data into a pandas DataFrame
df = pd.read_sql(sql_query, connection)


st.write(df)