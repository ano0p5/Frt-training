import requests
import json
from parsel import Selector
from pymongo import MongoClient

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "lidl"
CATEGORY_COLLECTION = "category_urls"
PRODUCT_COLLECTION = "products"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
category_collection = db[CATEGORY_COLLECTION]
product_collection = db[PRODUCT_COLLECTION]

# Fetch URLs from MongoDB
urls = [doc["url"] for doc in category_collection.find({}, {"url": 1})]

# Headers to mimic a real browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Iterate through each URL and scrape data
for url in urls:
    print(f"Scraping: {url}")
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        continue

    selector = Selector(response.text)

    for product in selector.xpath('//li[starts-with(@id, "product_")]'):
        data_str = product.xpath('./div/@data-grid-data').get()

        if data_str:
            try:
                data = json.loads(data_str.replace('&quot;', '"'))

                category_path = str(data.get("category", ""))
                breadcrumb = category_path.replace("/", " > ") if category_path else ""

                base_url = "https://www.lidl.nl"
                canonical_path = str(data.get("canonicalPath", ""))
                pdp_url = f"{base_url}{canonical_path}" if canonical_path else ""

                product_details = {
                    "title": str(data.get("fullTitle", "")),
                    "regular_price": str(data.get("price", {}).get("price", "")),
                    "selling_price": str(data.get("price", {}).get("price", "")),
                    "currency": str(data.get("price", {}).get("currencyCode", "")),
                    "brand": str(data.get("brand", {}).get("name", "")),
                    "category": category_path,  
                    "breadcrumb": breadcrumb, 
                    "pdp_url": pdp_url,
                    "image": str(data.get("image", "")),
                    "ratings": str(data.get("ratings", {}).get("average", "")),
                    "Instock": "TRUE" if data.get("stockAvailability", {}).get("onlineAvailable", False) else "FALSE"
                }

                # Insert into MongoDB (Avoid duplicate entries using pdp_url)
                product_collection.update_one(
                    {"pdp_url": pdp_url}, 
                    {"$set": product_details}, 
                    upsert=True
                )

                print(f"Saved: {product_details['title']}")

            except json.JSONDecodeError:
                print("Error parsing JSON for product")
