from parsel import Selector
from pymongo import MongoClient


file_path = '/home/anoop/frt/2025-04-09/Boodschappen _ Dirk.html'
with open(file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

selector = Selector(text=html_content)


client = MongoClient("mongodb://localhost:27017/")
db = client["dirk"]
collection = db["category_urls"]


departments = selector.css('a.department')

for dept in departments:
    category_url = dept.css('::attr(href)').get()
    category_name = dept.css('h3::text').get().strip()

    data = {
        "category_name": category_name,
        "url": category_url
    }

    collection.update_one({"url": category_url}, {"$set": data}, upsert=True)

print(f"{len(departments)} categories saved to MongoDB.")
