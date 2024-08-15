import streamlit as st
import pandas as pd
import openai
import os
import io
from io import StringIO
import gspread
import requests
from google.cloud import storage
import json
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
#from google_auth_oauthlib.flow import InstalledAppFlow
#from googleapiclient.discovery import build
#from googleapiclient.errors import 
import pymongo
from pymongo import MongoClient
import boto3
from botocore.exceptions import NoCredentialsError
#from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage,HumanMessage,SystemMessage
from dotenv import load_dotenv
load_dotenv()
# Setup OpenAI API Key
#with open('apikey.txt','r') as file:
#    openai.api_key = file.read()
openai.api_key = os.environ.get('openai_key')

sheet_id=os.environ.get('sheet_id')
sheet_name= ['LEAD','USERS', 'RATIOS','COMPANY DATA', 'FINANCIAL DATA']#"leads"
url_csv="https://docs.google.com/spreadsheets/d/{}/gviz/tq?tqx=out:csv&sheet={}"
# Function to fetch Google Sheet data and convert it to a DataFrame

def fetch_google_sheet():#(sheet_url):
    csv_url = url_csv.format(sheet_id,sheet_name[4]) #sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
    response = requests.get(csv_url)
    response.raise_for_status()  # Ensure the request was successful
    df = pd.read_csv(io.StringIO(response.text))
    #df = pd.read_excel('financial_gpt.xlsx',sheet_name=sheet_name[4])
    return df

# Function to convert DataFrame to CSV and provide download link
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

df = fetch_google_sheet()


# Initialize Boto3 S3 client
s3 = boto3.client('s3', aws_access_key_id=os.environ.get('aws_access_key_id'), aws_secret_access_key=os.environ.get('aws_secret_access_key'))

def upload_to_s3(file, bucket_name, object_name):
    try:
        s3.upload_fileobj(file, bucket_name, object_name)
        return True
    except NoCredentialsError:
        st.error("Credentials not available")
        return False
#AZURE_STORAGE_CONNECTION_STRING = "your_connection_string_here"
#CONTAINER_NAME = "your_container_name_here"

#def upload_to_azure(file, container_name):
#    try:
#        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
#        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file.name)

#        blob_client.upload_blob(file.getbuffer(), overwrite=True)
#        return True
#    except Exception as e:
#        st.error(f"Failed to upload to Azure: {e}")
#        return False
# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def save_uploaded_file(uploaded_file):
        with open(os.path.join('tempDir', uploaded_file.name), 'wb') as f:
            f.write(uploaded_file.getbuffer())
        return st.success('Saved file:{} in tempDir'.format(uploaded_file.name))



def register_user(email,company,username, password):
    # Simulate storing user data securely
    user_data = {'email': email,'company':company,'username': username, 'password': password}
    st.session_state.user_data = user_data
    st.session_state.authenticated = True

def authenticate_user(username, password):
    # Simulate user authentication
    client = MongoClient('mongodb+srv://{}:{}@users.eeaisqu.mongodb.net/'.format(os.environ.get('mongo_username'),os.environ.get('mongo_password')))
    db = client['tech_app_test']
    collection = db['users']
    user_data = collection.find_one({'username': username, 'password': password})
    if user_data:# in st.session_state:
        #if st.session_state.user_data['username'] == username and st.session_state.user_data['password'] == password:
        st.session_state.user_data = user_data
        st.session_state.authenticated = True
        #st.success("User authenticated successfully")
    else:
        st.warning("Invalid credentials")

def logout_user():
    st.session_state.authenticated = False


# User Registration and Authentication
if not st.session_state.authenticated:
    st.sidebar.title("User Authentication")
    auth_choice = st.sidebar.selectbox("Choose Action", ["Login", "Register"])

    if auth_choice == "Register":
        email = st.sidebar.text_input('Email')
        company = st.sidebar.text_input('Company')
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Register"):
            register_user(email, company, username, password)
            scope = ['https://spreadsheets.google.com/feeds', 'hthttps://docs.google.com/spreadsheets/dtps://www.googleapis.com/auth/drive']

            sheet_id2= os.environ.get('sheet_id2')
            #url_csv2= r'https://docs.google.com/spreadsheets/d/{}/edit?usp=sharing&ouid=114293662790834307704&rtpof=true&sd=true'
            #url_csv2 = r'/{}/gviz/tq?tqx=out:csv&sheet={}'
            #url_csv2 = r'https://docs.google.com/v4/spreadsheets/{}/values/{}:append'
            #credentials = storage.Client.from_service_account_json(r'lunar-mission-292701-ce6a5fb4ca50.json')
            #credentials = service_account.Credentials.from_service_account_file(r'lunar-mission-292701-ce6a5fb4ca50.json', scope=scope)
            #client = gspread.authorize(credentials)
            #urlb2= 'https://storage.googleapis.com/upload/storage/v1/b/test_app_fintech_streamlit/o'
            # Open the Google Sheet by its title
            #sheet = client.open('financial_gpt')

            # Select the worksheet by its title
            #worksheet2 = sheet_name[1]#sheet.worksheet(sheet_name[1])
            
            #worksheet3 = sheet.worksheet(worksheet2)
            #num_rows = len(worksheet3.get_all_values())
            # Get the last ID from the first column
            #existing_values = requests.get(url_csv.format(sheet_id,worksheet2))#access_token)
    
            #Find the next ID
            #if not num_rows:
            #    next_id = 1
            #else:
            #    last_row = num_rows[-1]
            #    last_id = int(last_row[0]) if last_row and last_row[0].isdigit() else 0
            #    next_id = last_id + 1 

            # Add the new registration data to the Google Sheet
            #data=[email,username,password]
            data = {'email':email, 'company':company,'username':username, 'password':password}
            json_string = json.dumps(data)
            #worksheet3.append_row(data)
            #response2 = requests.post(urlb2, json=json_string)
            #response2 = requests.post(url_csv2.format(sheet_id2,worksheet2), json=json_string)
            #response2.raise_for_status() 
            #response2.append(data)
            client = MongoClient('mongodb+srv://{}:{}@users.eeaisqu.mongodb.net/'.format(os.environ.get('mongo_username'),os.environ.get('mongo_password')))
            db = client['tech_app_test']
            collection = db['users'] 
            result = collection.insert_one(data)

            st.success("User registered successfully")

    if auth_choice == "Login":
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            authenticate_user(username, password)
            if st.session_state.authenticated:
                st.success("User authenticated successfully")
        


# End User Section
if st.session_state.authenticated:
    st.sidebar.button("Logout", on_click=logout_user)

    st.title("Bitbond.com.mx")

    # Chatbot Integration
    st.subheader("Chat with our AI")
    url = 'https://chatgpt.com/g/g-zL5o4nHMj-customer-experience' #'https://chatgpt.com/g/g-VP9UTAz2c-financial-analyst-assistant'
    user_input = st.text_area("Puedes chatear con nuestro asistente: ")
    chat = ChatOpenAI(api_key=openai.api_key)


    if st.button("Send", key=1):
        
        #url = 'https://chatgpt.com/g/g-VP9UTAz2c-financial-analyst-assistant'

        response = openai.chat.completions.create(
            model= 'gpt-4',
            temperature=0.5,
            stream=False,
            messages=[
            {"role": "system", "content": url},
            {'role':'user','content':user_input}
            ]
        )
        response = response.choices[0].message.content
        #response = openai.Completion.create(
        #    engine="text-davinci-002",
        #    prompt=user_input,
        #    max_tokens=150
        #)
        #st.text_area("GPT Response:", response)#response.choices[0].text)
        response_placeholder = st.empty()
        response_placeholder.write(response)

        #st.experimental_rerun()
        
    # Download CSV Template
    st.subheader("Download CSV Template")
    df = fetch_google_sheet()
    #st.dataframe(df)  # Display the DataFrame in Streamlit

    csv = convert_df_to_csv(df)
    template_csv = csv#"Column1,Column2,Column3\nValue1,Value2,Value3"
    st.download_button(
        label="Download CSV template",
        data=template_csv,
        file_name='template.csv',
        mime='text/csv'
    )

    
    # File Uploads
    st.subheader("Upload Files")
    pdf_file = st.file_uploader("Upload PDF files", type=["pdf"])
    csv_file = st.file_uploader("Upload CSV files", type=["csv"])

    uploaded_files = []
    # Save uploaded files
    if pdf_file is not None:
        with open(os.path.join("", pdf_file.name), "wb") as f:
            f.write(pdf_file.getbuffer())
        st.success(f"Uploaded {pdf_file.name}")
        uploaded_files.append(pdf_file)
        #username = st.text_input("Type Username to confirm to send")

    if csv_file is not None:
        with open(os.path.join('', csv_file.name), "wb") as f:
            f.write(csv_file.getbuffer())
        st.success(f"Uploaded {csv_file.name}")
        uploaded_files.append(csv_file)
        #username = st.text_input("Type Username to confirm to send")
     # Upload to AWS Storage
    company = st.text_input("Type Your Company's Name to confirm to send")

    if st.button("Send"):
        if not uploaded_files:
            st.warning("No files to upload")
        else:
            bucket_name = 'streamlit-fintech-app'
            
            for file in uploaded_files:
                object_name = 'users-info/{}/{}'.format(company, file.name)
                if upload_to_s3(file, bucket_name, object_name):
                    st.success(f"Successfully sent {file.name}")
                else:
                    st.error(f"Failed to upload {file.name}")

