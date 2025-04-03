import requests
import json
from parsel import Selector
from pymongo import MongoClient

BASE_URL = "https://www.marksandspencer.com"
url = "https://www.marksandspencer.com/c/women"
headers = {"User-Agent": "Mozilla/5.0"}

client = MongoClient("mongodb://localhost:27017/")
db = client["m_and_s"]
collection = db["category_urls"]

response = requests.get(url, headers=headers)
selector = Selector(response.text)
script_data = selector.xpath('//script[@id="__NEXT_DATA__"]/text()').get()

if script_data:
    json_data = json.loads(script_data)
    categories = json_data.get("props", {}).get("appProps", {}).get("headerProps", {}).get("navigationData", {}).get("categories", [])
    
    extracted_urls = []
    stop_keyword = "Trousers"

    for category in categories:
        for sublist in category.get("items", []):
            for subcategory in sublist:
                for sub in subcategory.get("items", []):
                    category_name = sub["name"]
                    category_url = sub.get("url", "")

                    if category_url and category_url.startswith("/"):
                        category_url = BASE_URL + category_url

                    extracted_urls.append({"category_name": category_name, "category_url": category_url})

                    if category_name == stop_keyword:
                        break
                if extracted_urls and extracted_urls[-1]["category_name"] == stop_keyword:
                    break
            if extracted_urls and extracted_urls[-1]["category_name"] == stop_keyword:
                break
        if extracted_urls and extracted_urls[-1]["category_name"] == stop_keyword:
            break

    if extracted_urls:
        collection.insert_many(extracted_urls)
