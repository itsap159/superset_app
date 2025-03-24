from flask import Flask, request, jsonify
import requests
import json
import jwt
import csv
import psycopg2
from pymongo import MongoClient
import os
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
CORS(app)  

# Configurations
# Superset configurations
BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

# Database configurations
SUPERSET_DB_NAME = os.getenv("SUPERSET_DB_NAME")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# MongoDB configurations
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME")

# Other configurations
TABLE_NAME = os.getenv("TABLE_NAME")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
CSV_FILENAME = os.getenv("CSV_FILENAME")

CA_BUNDLE = False

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# MongoDB Connection
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB_NAME]
mongo_collection = mongo_db[MONGO_COLLECTION_NAME]

def store_file_in_mongo(file_path):
    """Deletes old data, then reads CSV and stores it in MongoDB"""
    mongo_collection.delete_many({})  # Deletes all existing records
    
    with open(file_path, "r") as file:
        csv_reader = csv.DictReader(file)
        mongo_collection.insert_many(list(csv_reader))
    
    return True


def fetch_and_store_csv():
    """Fetches data from MongoDB and writes it to a CSV file"""
    data = list(mongo_collection.find())
    clean_data = [{k: v for k, v in doc.items() if k != "_id"} for doc in data]
    
    fieldnames = sorted(set().union(*(d.keys() for d in clean_data)))
    
    with open(CSV_FILENAME, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in clean_data:
            writer.writerow({field: row.get(field, "") for field in fieldnames})
    
    return True

def store_csv_to_postgres():
    """Stores CSV data into PostgreSQL, creating a new empty table each time"""
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    cursor = conn.cursor()
    
    # Drop the table if it exists
    drop_table_query = f'DROP TABLE IF EXISTS {TABLE_NAME};'
    cursor.execute(drop_table_query)
    
    # Create a new table
    with open(CSV_FILENAME, "r") as file:
        header = file.readline().strip().split(",")
        column_definitions = ", ".join([f'"{col}" TEXT' for col in header])
        create_table_query = f'CREATE TABLE {TABLE_NAME} ({column_definitions});'
        cursor.execute(create_table_query)
    
    # Copy data from CSV to the new table
    with open(CSV_FILENAME, "r") as file:
        next(file)  # Skip header as it will be used in the COPY command
        cursor.copy_expert(f"COPY {TABLE_NAME} FROM STDIN WITH CSV HEADER", file)
    
    conn.commit()
    cursor.close()
    conn.close()
    return True

def login(base_url, username, password):
    '''Responsible for collecting the access token and correcting it to get the CSRF token.'''
    url = base_url + 'api/v1/security/login'
    payload = {'password': password, 'provider': 'db', 'refresh': 'true', 'username': username}
    payload_json = json.dumps(payload)
    headers = {'Content-Type': 'application/json'}
    try:
        res = requests.post(url, data=payload_json,
                            verify=CA_BUNDLE, headers=headers)
        res.raise_for_status()
        access_token = res.json()['access_token']
        refresh_token = res.json()['refresh_token']
        print("SUCCESS")
        # header = jwt.get_unverified_header(token)
        # print(header)

        decoded_token = jwt.decode(access_token, options={"verify_signature": False})

        decoded_token["sub"] = str(decoded_token["sub"])
        print(os.getenv("SECRET_KEY"))
        SECRET_KEY=os.getenv('SECRET_KEY')

        access_token = jwt.encode(decoded_token, SECRET_KEY, algorithm="HS256")

        print("New Signed Token:", access_token)

        return access_token, refresh_token

    except requests.exceptions.RequestException as err:
        print("Request Exception:", err)
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)

def get_database_id(base_url, access_token, database_name, session):
    """Get database ID by name"""
    databases_url = base_url + 'api/v1/database/'
    # Get list of databases
    response = session.get(databases_url, verify=CA_BUNDLE)
    
    if response.status_code != 200:
        print(f"Failed to get databases: {response.text}")
        return None
    
    databases = response.json()['result']
    
    # Find the database by name
    for db in databases:
        if db['database_name'] == database_name:
            return db['id']
        
def create_dataset(base_url, access_token, database_id, table_name, session):
    """Create a dataset in Superset"""
    dataset_url = base_url + 'api/v1/dataset/'
    
    payload = {
        "database": database_id,
        "schema": 'public',  # Change this if your table belongs to a schema
        "table_name": table_name
    }
    
    response = session.post(dataset_url, json=payload, verify=CA_BUNDLE)
    
    if response.status_code == 201:
        return response.json()['id']
    else:
        print(f"Failed to create dataset: {response.text}")
        return None

def create_database(base_url, access_token,
                    superset_database_name, database_name, database_port, database_host,
                    database_user, database_password):
    '''Gets the CSRF token and creates a database.'''
    csrf_url = base_url + 'api/v1/security/csrf_token/'
    headers = {'Authorization': 'Bearer ' + access_token}

    url = base_url + 'api/v1/database'

    payload = {
        "database_name": superset_database_name,
        "engine": "postgresql",
        "configuration_method": "sqlalchemy_form",
        "sqlalchemy_uri": "postgresql+psycopg2://{}:{}@{}:{}/{}".\
            format(database_user, database_password, database_host, database_port, database_name)
        }
    payload_json = json.dumps(payload)
    try:
        session = requests.Session()
        session.headers['Authorization'] = 'Bearer ' + access_token
        session.headers['Content-Type'] = 'application/json'
        csrf_res = session.get(csrf_url, verify=CA_BUNDLE)
        print(csrf_res.json())
        session.headers['Referer']= csrf_url
        session.headers['X-CSRFToken'] = csrf_res.json()['result']
        res = session.post(url, data=payload_json, verify=CA_BUNDLE)
        database_id = get_database_id(base_url, access_token, superset_database_name, session)
        dataset = create_dataset(BASE_URL, access_token, database_id, TABLE_NAME, session)
        res.raise_for_status()

    except requests.exceptions.RequestException as err:
        print("Request Exception:", err)
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        store_file_in_mongo(file_path)

        fetch_and_store_csv()
        store_csv_to_postgres()

        access_token, refresh_token = login(BASE_URL, USERNAME, PASSWORD)
        create_database(BASE_URL, access_token, SUPERSET_DB_NAME, DB_NAME, DB_PORT, DB_HOST,
                    DB_USER, DB_PASSWORD)

        return jsonify({"message": "Data successfully migrated and Superset database created!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask app...") 
    app.run(debug=True)
