from pymongo import MongoClient
import json

with open('FrequentFlyerForum-Profiles.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

client = MongoClient('mongodb://localhost:27017/')
db = client['airlines']
collection = db['forum_profiles']

forum_profiles = data.get('Forum Profiles', [])

if forum_profiles:
    collection.insert_many(forum_profiles)
else:
    print("Данные в ключе 'Forum Profiles' отсутствуют.")
