import pymongo
from parsel import Selector

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "dirk"
COLLECTION_NAME = "subcategory_urls"

client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

file_path = '/home/anoop/frt/2025-04-09/Zuivel & kaas _ Dirk.html'

with open(file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

selector = Selector(text=html_content)

subcategory_links = selector.css('div.right nav ul li a')

for link in subcategory_links:
    subcategory_url = link.css('::attr(href)').get().strip()
    name = link.css('::text').get().strip()

    document = {
        "category_name": name,
        "url": subcategory_url
    }

    collection.insert_one(document)

    print({"category_name": name, "url": subcategory_url})
