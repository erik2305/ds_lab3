from pymongo import MongoClient
import json

with open('bp_bd_sirena_merge.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

client = MongoClient('mongodb://192.168.31.27:27017/')  
db = client['airlines']  
collection = db['Passenger']  

documents = []

for passenger_id, passenger_data in data.items():
    passenger_data['_id'] = passenger_id
    documents.append(passenger_data)

if documents:
    collection.insert_many(documents)
    print(f"Successfully inserted {len(documents)} documents.")
else:
    print("No data found to insert.")
