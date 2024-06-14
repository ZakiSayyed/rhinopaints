import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import altair as alt
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from collections import defaultdict
import time

st.set_page_config(
    page_title='Rhino Paints',
    page_icon=':shopping_bags:',
    layout="wide"
)

menu = ["Inventory", "Units Left", "Best Seller"]

# Use the index of the default choice in the options list
default_index = 0  # Index of "Login" in menu (starts from 0)
choice = st.sidebar.selectbox("Menu", menu, index=default_index)

def load_inventory_data():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict({
        "type": "service_account",
        "project_id": st.secrets["google_sheets"]["project_id"],
        "private_key_id": st.secrets["google_sheets"]["private_key_id"],
        "private_key": st.secrets["google_sheets"]["private_key"],
        "client_email": st.secrets["google_sheets"]["client_email"],
        "client_id": st.secrets["google_sheets"]["client_id"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": st.secrets["google_sheets"]["client_x509_cert_url"]
    }, scope)
    client = gspread.authorize(creds)
    sheet_id = '1Bsv2n_12_wmWhNI5I5HgCmBWsVyAHFw3rfTGoIrT5ho'
    sheet = client.open_by_key(sheet_id).get_worksheet(2)
    sheet_data = sheet.get_all_values()
    
    return pd.DataFrame(sheet_data[1:], columns=sheet_data[0])

def update_google_sheet(df):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict({
        "type": "service_account",
        "project_id": st.secrets["google_sheets"]["project_id"],
        "private_key_id": st.secrets["google_sheets"]["private_key_id"],
        "private_key": st.secrets["google_sheets"]["private_key"],
        "client_email": st.secrets["google_sheets"]["client_email"],
        "client_id": st.secrets["google_sheets"]["client_id"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": st.secrets["google_sheets"]["client_x509_cert_url"]
    }, scope)
    client = gspread.authorize(creds)
    sheet_id = '1Bsv2n_12_wmWhNI5I5HgCmBWsVyAHFw3rfTGoIrT5ho'
    sheet = client.open_by_key(sheet_id).get_worksheet(2)

    # Clear existing data
    sheet.clear()

    # Update with new data
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

# Load data
data = load_inventory_data()

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = data.copy()

# Display title
st.markdown("<h1 style='text-align: center;'>Rhino Paints</h1>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)

if choice == 'Inventory':
    st.header("Inventory")
    if st.button("Refresh"):
        with st.spinner("Refreshing Data"):
            time.sleep(3)
            st.session_state.data = load_inventory_data() 
            st.success("Data refreshed successfully!")
            time.sleep(3)
            st.rerun()

    # Display editable DataFrame
    edited_df = st.data_editor(st.session_state.data)

    # Handle commit changes
    if st.button("Commit"):
        update_google_sheet(edited_df)
        st.session_state.data = edited_df.copy()
        st.success("Changes have been committed to Google Sheets.")

    # Option to add a new row
    if st.button("Add new row"):
        new_row = pd.DataFrame({col: "" for col in edited_df.columns}, index=[0])
        st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
        st.rerun()  # Rerun to update the interface with the new row

elif choice == 'Units Left':
    st.subheader('Items left', divider='red')

    if st.button("Refresh"):
        with st.spinner("Refreshing Data"):
            time.sleep(3)
            st.session_state.data = load_inventory_data() 
            st.success("Data refreshed successfully!")
            time.sleep(3)
            st.rerun()

    data['Units left'] = data['Units left'].astype(int)
    data['Reorder point'] = data['Reorder point'].astype(int)

    need_to_reorder = data[data['Units left'] <= data['Reorder point']]
    if not need_to_reorder.empty:
        items = '\n'.join(f'* {row["Item Name"]}: {row["Units left"]} units left' for idx, row in need_to_reorder.iterrows())
        st.error(f"We're running dangerously low on the items below:\n{items}")
        
    st.altair_chart(
        # Layer 1: Bar chart.
        alt.Chart(data)
            .mark_bar(
                orient='horizontal',
            )
            .encode(
                x='Units left',
                y='Item Name',
            )
        # Layer 2: Chart showing the reorder point.
        + alt.Chart(data)
            .mark_point(
                shape='diamond',
                filled=True,
                size=50,
                color='salmon',
                opacity=1,
            )
            .encode(
                x='Reorder point',
                y='Item Name',
            )
        ,
        use_container_width=True)

    st.caption('NOTE: The :diamonds: location shows the reorder point.')

elif choice == 'Best Seller':
    st.subheader('Best sellers', divider='orange')
    if st.button("Refresh"):
        with st.spinner("Refreshing Data"):
            time.sleep(3)
            st.session_state.data = load_inventory_data() 
            st.success("Data refreshed successfully!")
            time.sleep(3)
            st.rerun()    

    ''
    ''

    st.altair_chart(
        alt.Chart(data)
            .mark_bar(orient='horizontal')
            .encode(
                x='Units sold:Q',
                y=alt.Y('Item Name:N', sort=alt.EncodingSortField(field='Units sold', order='descending'))
            ),
        use_container_width=True
    )
