from pymongo import MongoClient
import json

with open('PointzAggregator-AirlinesData.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

client = MongoClient('mongodb://localhost:27017/')
db = client['airlines']
collection = db['airlines_data']

forum_profiles = data.get("PointzAggregatorUsers").get('user', [])

if forum_profiles:
    collection.insert_many(forum_profiles)
else:
    print("Данные в ключе 'Forum Profiles' отсутствуют.")
