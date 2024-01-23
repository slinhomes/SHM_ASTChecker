import streamlit as st
import pyodbc
import pandas as pd

# Function to connect to the Azure SQL database
def create_connection():
    server = 'studenthomesmgmt.database.windows.net'
    database = 'PortfolioManagement'
    username = st.secrets['db_username']
    password = st.secrets['db_password']
    driver = '{ODBC Driver 17 for SQL Server}'  # Adjust the driver if needed
    conn = pyodbc.connect(
        f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
    return conn

# Function to create table
def create_table(conn):
    try:
        sql = '''CREATE TABLE [dbo].[SHMASTCheck] (
                [Dwelling_ID] NVARCHAR(50) NULL,
                [Academic_Year] NVARCHAR(50) NULL,
                [Checked_By] NVARCHAR(MAX) NULL,
                [Comment] NVARCHAR(MAX) NULL
            );'''
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print(e)

# Function to insert data 
def insert_data(conn, data):
    insert_sql = '''INSERT INTO SHMASTCheck (Dwelling_ID, Academic_Year, Checked_by, Comment)
                   VALUES (?, ?, ?, ?);'''

    cur = conn.cursor()
    cur.execute(insert_sql, data)
    conn.commit()

def show():
    st.write("SHM AST checker")
    st.markdown("---")

    # Connect to the database and fetch property addresses and IDs
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Dwelling_ID, flat_number, property_address, city FROM SHMDwellingInfo")
    rows = cursor.fetchall()
    property = {f'{row[1]} {row[2]}, {row[3]}': (row[0]) for row in rows}  # Mapping detailed address to DwellingID

    # Dropdown for selecting asset address
    selected_property = st.selectbox("Property", ["Select property"] + list(property.keys()))

    # Check if a detailed address is selected
    if selected_property != "Select property":
        # Display Dwelling ID and full address if a detailed address is selected
        dwelling_id = property[selected_property]
        st.caption(f"Dwelling ID: {dwelling_id}")
    else:
        dwelling_id = 'Dwelling does not exist, please check your selection.'

    # Dropdown for selecting AY
    ay = st.selectbox("Academic year", ["2023", "2024", "2025", "2026"])

    # Dropdown for selecting a requirements or condition
    checked_by = st.selectbox("AST checked by", ['MG','FR','GB'])

    # Text input for comments
    comments = st.text_area("Comments for AST", placeholder="Please add in any comments you'd like to leave against the AST", height=100)

    data = {
        "Dwelling_ID" : dwelling_id,
        "Academic_Year": ay,
        "Checked_By": checked_by,
        "Comment": comments
    }

    preview_df = pd.Dataframe([data]).set_index('Dwelling_ID')
    st.data_editor(preview_df,
                   column_config = {
                       "Dwelling_ID": st.column_config.TextColumn("Dwelling ID"),
                       "Academic_Year": st.column_config.TextColumn("Academic year"),
                       "Checked_By": st.column_config.TextColumn("Checked by"),
                       "Comment": st.column_config.TextColumn("Comments")
                   }, hide_index=True,
                   disabled = ["Dwelling_ID","Academic_Year","Checked_By","Comment"])

    submit_button = st.button("Submit")
    if submit_button:
        data_tuple = (
            dwelling_id, ay, checked_by, comments
        )

        conn = create_connection()
        create_table(conn)

        try:
            insert_data(conn, data_tuple)
            st.success("Data submitted successfully!")
        except Exception as e:
            st.error(f"An error occurred: {e}")

        conn.close()









