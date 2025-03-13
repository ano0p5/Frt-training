import requests
import pymongo
from parsel import Selector
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

class Crawler:
    def __init__(self):
        self.client = pymongo.MongoClient()
        self.db = self.client["Next_DB"]
        self.collection = self.db["Category_urls"]
        self.product_collection = self.db["Product_urls"]
        self.urls = self.collection.find_one().get("urls", [])

    def extract_product_urls(self, page_url):
        try:
            response = requests.get(page_url)
            if response.status_code == 200:
                selector = Selector(response.text)
                product_urls = selector.xpath('//a[contains(@class, "MuiCardMedia-root")]/@href').getall()
                full_urls = [url if url.startswith("http") else f"https://www.next.co.uk{url}" for url in product_urls]
                return full_urls
            return []
        except requests.RequestException as e:
            logging.error(f"Error accessing {page_url}: {e}")
            return []

    def crawl(self):
        all_product_urls = set() 
        for base_url in self.urls:
            logging.info(f"Processing Category URL: {base_url}")
            for page in range(1, 41):
                paginated_url = f"{base_url[:-1]}{page}#480"
                logging.info(f"Fetching from: {paginated_url}")
                product_urls = self.extract_product_urls(paginated_url)
                all_product_urls.update(product_urls)  
            logging.info(f"Total unique products collected from {base_url}: {len(all_product_urls)}")
        
        if all_product_urls:
            self.product_collection.delete_many({})
            self.product_collection.insert_one({"urls": list(all_product_urls)})  
            logging.info(f"Inserted {len(all_product_urls)} unique product URLs into the database.")

if __name__ == "__main__":
    crawler = Crawler()
    crawler.crawl()
