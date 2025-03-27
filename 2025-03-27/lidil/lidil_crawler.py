import requests
from parsel import Selector
from pymongo import MongoClient

class LidlCategoryScraper:
    def __init__(self):
        self.headers = {
            "referer": "https://www.lidl.nl/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.base_url = "https://www.lidl.nl/c/assortiment-producten/s10008015"
        self.target_categories = {
            "Kazen": "Cheese",
            "Zuivel, plantaardig en eieren": "Dairy, plant-based and eggs"
        }
        self.filtered_categories = []
        self.scrape_categories()

    def scrape_categories(self):
        response = requests.get(self.base_url, headers=self.headers)
        if response.status_code == 200:
            selector = Selector(response.text)
            for item in selector.css("li.ATheContentPageCardList__Item"):
                category_name = item.css("h3.ATheContentPageCard__Claim::text").get()
                category_url = item.css("a.ATheContentPageCardList__Item--linked::attr(href)").get()
                
                if category_name and category_url:
                    category_name = category_name.strip()
                    if category_name in self.target_categories:
                        self.filtered_categories.append({
                            "name": self.target_categories[category_name],
                            "url": category_url 
                        })

    def get_categories(self):
        return self.filtered_categories


class LidlProductScraper:
    def __init__(self, category_name, category_url, headers):
        self.category_name = category_name
        self.category_url = category_url
        self.headers = headers
        self.base_url = "https://www.lidl.nl"
        self.products = []

    def scrape_products(self):
        response = requests.get(self.category_url, headers=self.headers)
        if response.status_code == 200:
            selector = Selector(response.text)
            for product in selector.xpath("//div[contains(@class, 'AProductGridbox__GridTilePlaceholder')]"):
                product_url = product.xpath(".//@canonicalpath").get()
                product_title = product.xpath(".//@fulltitle").get()

                if product_url and product_title:
                    self.products.append({
                        "category": self.category_name,
                        "product_name": product_title.strip(),
                        "product_url": self.base_url + product_url,
                    })

    def get_products(self):
        return self.products


# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["lidl"]
collection = db["crawler"]

scraper = LidlCategoryScraper()
categories = scraper.get_categories()

for category in categories:
    print(f"Scraping: {category['name']} ({category['url']})")
    product_scraper = LidlProductScraper(category["name"], category["url"], scraper.headers)
    product_scraper.scrape_products()
    products = product_scraper.get_products()

    if products:
        collection.insert_many(products)
        print(f"Inserted {len(products)} products into the database.")
    else:
        print("No products found.")
