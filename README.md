# Superset App

A web application that allows users to upload CSV files, process the data through a pipeline involving MongoDB and PostgreSQL, uploading the data to superset.

## Project Overview

This application provides a simple interface for users to upload CSV files, which are then:
1. Stored in MongoDB
3. Transferred to PostgreSQL
4. Connected to Apache Superset for visualization and analytics

## Features

- User-friendly CSV file upload interface
- Automatic integration with Superset

## Technology Stack

### Frontend
- React.js

### Backend
- Flask (Python)
- MongoDB (NoSQL database)
- PostgreSQL (SQL database)
- Apache Superset (Data visualization platform)

## Prerequisites

Before setting up this project, make sure you have the following installed:

- npm (for React frontend)
- Python 3.7+ (for Flask backend)
- MongoDB (running locally or accessible instance)
- PostgreSQL (running locally or accessible instance)
- Apache Superset (setup and running)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/itsap159/superset_app.git
cd superset_app
```

### 2. Backend

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```
## .env 

``` bash
# Superset configurations
BASE_URL=
USERNAME=
PASSWORD=

# Database configurations
SUPERSET_DB_NAME=
DB_NAME=
DB_PORT=
DB_HOST=
DB_USER=
DB_PASSWORD=

# MongoDB configurations
MONGO_URI=
MONGO_DB_NAME=
MONGO_COLLECTION_NAME=

# Other configurations
TABLE_NAME=
UPLOAD_FOLDER=
CSV_FILENAME=
SECRET_KEY=
```

### 3. Frontend

```bash
# Navigate to the csv-uploader directory
cd csv-uploader

# Install dependencies
npm install
```

## Running the Application
### 1. Start the Backend
```bash
# From the backend directory with virtual environment activated
python app.py
```
The Flask backend will start on http://127.0.0.1:5000

### 2. Start the Frontend
```bash
# From the csv-uploader directory
npm start
```
The React frontend will start on http://localhost:3000

### 3. Ensure Databases are Running
- Make sure MongoDB is running on the specified URI in your .env file

- Make sure PostgreSQL is running and accessible with the credentials in your .env file

### 4. Ensure Superset is Running
- Apache Superset should be running on http://127.0.0.1:8088 or the URL specified in your .env file

## Requirements
### 1. Python Dependencies
### 2. MongoDB Setup
- Install MongoDB Community Edition
- Start the MongoDB service
- No special configuration is needed; the application will create the necessary database and collection

### 3. PostgreSQL Setup
- Install PostgreSQL
- Create a database that matches the DB_NAME in your .env file or use default.
- Ensure the user has permissions to create and modify tables

### 4. Superset Setup
- Install Apache Superset following the official documentation
- Create an admin user that matches the USERNAME and PASSWORD in your .env file

## Usage
- Access the web interface at http://localhost:3000

- Upload a CSV file using the provided interface

- The application will process the file through the pipeline

- Once complete, you will be redirected to Superset to start creating visualizations



