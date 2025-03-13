import requests
import pymongo

class NextCrawler:
    def __init__(self):
        self.url = "https://www.next.co.uk/secondary-items/home/women"
        self.base_url = "https://www.next.co.uk"
        self.pagination_suffix = "?p=0"
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.collection = self.client["Next_DB"]["Category_urls"]

    def find_all_clothing(self, obj):
        targets = []
        if isinstance(obj, dict):
            if obj.get("title") == "All Clothing" and "items" in obj:
                for item in obj["items"]:
                    if "target" in item:
                        full_url = f"{self.base_url}{item['target']}{self.pagination_suffix}"
                        targets.append(full_url)
            for value in obj.values():
                targets.extend(self.find_all_clothing(value))
        elif isinstance(obj, list):
            for item in obj:
                targets.extend(self.find_all_clothing(item))
        return targets

    def save_to_db(self, urls):
        if urls:
            self.collection.insert_one({"urls": urls})
            print(f"Saved {len(urls)} URLs to the database.")

    def crawl(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            urls = self.find_all_clothing(response.json())
            self.save_to_db(urls)
            print("Crawling completed.")
        else:
            print(f"Failed to retrieve data: {response.status_code}")

crawler = NextCrawler()
crawler.crawl()
