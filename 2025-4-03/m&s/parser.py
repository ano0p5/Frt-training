import requests
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["m_and_s"]
collection = db["category_urls"]

urls = collection.find({}, {"category_url": 1, "_id": 0})

for url_data in urls:
    url = url_data["category_url"]
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    print(f"{url} - {response.status_code}")
