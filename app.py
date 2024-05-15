from flask import Flask
import certifi
import requests
import json
from datetime import datetime, timedelta
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
# https://help.pythonanywhere.com/pages/MongoDB/
from requests.auth import HTTPDigestAuth

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


def get_public_ip():

    response = requests.get('https://api.ipify.org')

    return response.text


def read_app_config():
    global app_config
    config_file = open('app_config.json')
    config_text = config_file.read()
    app_config = json.loads(config_text)
    

@app.route('/mongo/get_admin_api_token')
def mongo_get_admin_api_token():
    
    read_app_config() 
    api_key_public = app_config["mongo"]["api_key_public"]
    api_key_private = app_config["mongo"]["api_key_private"]

    uri = 'https://services.cloud.mongodb.com/api/admin/v3.0/auth/providers/mongodb-cloud/login'
    data = json.dumps( {"username": api_key_public, "apiKey": api_key_private})
    header = {
         'Content-Type': 'application/json'
         'Accept': 'application/json'
    }
    return requests.post(uri,data)
  
    # https://www.mongodb.com/docs/atlas/app-services/admin/api/v3/#section/Project-and-Application-IDs
    """
        curl --request POST \
        --header 'Content-Type: application/json' \
        --header 'Accept: application/json' \
        --data '{"username": "<Public API Key>", "apiKey": "<Private API Key>"}' \
        https://services.cloud.mongodb.com/api/admin/v3.0/auth/providers/mongodb-cloud/login

    """

@app.route('/mongo/add_ip_address')
def add_ip_address():
    
    read_app_config() 
    # Your Atlas API credentials and project/app IDs
    api_key_public =  app_config["mongo"]["api_key_public"]
    api_key_private = app_config["mongo"]["api_key_private"]
    app_id =app_config["mongo"]["application_id"]
    group_id = app_config["mongo"]["project_id"]
    delete_after_datetime = datetime.utcnow() + timedelta(days=7)
    delete_after_date_str = delete_after_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")

    # IP address and optional comment
    ip_address = "75.75.184.203"
    comment = "Added for accessing application"

    # API endpoint
    url = f"https://cloud.mongodb.com/api/atlas/v2/groups/{group_id}/accessList"
        
    # Headers with API keys
    headers =  {
        "accept": "application/vnd.atlas.2023-02-01+json",
        "Content-Type": "application/json"
    } 

    # Data payload for the new IP address
    data = [ {
        "ipAddress": ip_address,
        "comment": comment
        
    }]

    # Send the POST request
    response = requests.post(url, auth=HTTPDigestAuth(api_key_public, api_key_private), headers=headers, json=data)

    # Check the response status
    if response.status_code == 201:
        return("IP address added successfully!")
    else:
        return(f"Error adding IP address: {response.status_code} - {response.text}")
    
"""$ApiPrivateKey 
$ApiPublicKey
$Uri = 'https://cloud.mongodb.com/api/atlas/v1.0/groups/{ORG-ID}/accessList?pretty=true'
[securestring]$secStringPassword = ConvertTo-SecureString $ApiPrivateKey -AsPlainText -Force
[pscredential]$credential = New-Object System.Management.Automation.PSCredential ($ApiPublicKey, $secStringPassword)
Invoke-RestMethod -Uri $Uri -ContentType Application/Json -Headers @{Authorization = “Basic $base64AuthInfo”} -Credential $credential -Method Get"""





@app.route('/mongo/test')
def add_allowed_ip():
    token = mongo_get_admin_api_token()
    return token

@app.route('/mongo_connect')
def mongo_connect():
    read_app_config()
    
    usr = app_config['mongo']['user_name']
    pas = app_config['mongo']['user_name']
    app_id = app_config['mongo']['application_id']
    cluster = app_config['mongo']['cluster']

    # Create a new client and connect to the server
    global mongo_client
    uri = f"mongodb+srv://{usr}:{"asdfasdf"}@{cluster}.d2woiba.mongodb.net/?retryWrites=true&w=majority&appName=cluster"

    mongo_client = MongoClient(uri, server_api = ServerApi('1'), tlsCAFile=certifi.where())
    try:
        mongo_client.list_database_names()
    except Exception as e:
        return (str(e))



@app.route('/get_ip')
def get_ip():
    return mongo_connect()

# ********************************
if __name__ == '__main__':
    app.run()



