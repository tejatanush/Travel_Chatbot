import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# MongoDB connection URI
uri = "mongodb+srv://tanush2:hVVs6seb1QOOUvjD@cluster0.bnl3hcv.mongodb.net/?appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Ping the server to check connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("Connection failed:", e)
    exit()

# Select database and collection
db = client["travel-db"]
collection = db["travel-images"]

# Load the JSON file
try:
    with open("links_json.json", "r") as file:
        data = json.load(file)
except Exception as e:
    print("Error reading JSON file:", e)
    exit()

# Function to normalize keywords (remove spaces, lowercase)
def normalize_keyword(keyword):
    return keyword.replace(" ", "").lower()

# Normalize keywords and add new field
def preprocess_document(doc):
    doc["normalized_keywords"] = [normalize_keyword(k) for k in doc.get("keywords", [])]
    return doc

# Apply preprocessing
if isinstance(data, list):
    processed_data = [preprocess_document(doc) for doc in data]
    collection.insert_many(processed_data)
else:
    processed_data = preprocess_document(data)
    collection.insert_one(processed_data)

print("Data inserted successfully with normalized keywords.")


