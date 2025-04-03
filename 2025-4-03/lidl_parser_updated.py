import logging
import requests
from parsel import Selector
import re
from datetime import datetime
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

class LidlScraper:
    def __init__(self, mongo_uri):
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client["lidl"]
        self.product_collection = self.db["products"]  
        self.final_collection = self.db["products_final"]  
        self.extraction_date = datetime.now().strftime("%Y-%m-%d")
        self.session = requests.Session()

    def fetch_product_urls(self):
        """Fetch product URLs from MongoDB `products` collection."""
        return [doc.get("pdp_url", "") for doc in self.product_collection.find({}, {"pdp_url": 1}) if doc.get("pdp_url")]

    def fetch_page(self, product_url):
        """Fetch the product page HTML and return a Selector object."""
        try:
            response = self.session.get(product_url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                return Selector(text=response.text)
            logger.error(f"Failed to fetch {product_url} - Status Code: {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"Request failed for {product_url}: {e}")
        return None

    def extract_product_data(self, selector, product_url):
        """Extracts product details."""
        breadcrumbs, breadcrumb_levels = self.extract_breadcrumbs(selector)  
        image_urls = self.extract_image_urls(selector) 
        unique_id = selector.xpath('//span[@class="product-id__number"]/text()').get() or ""

        self.product_data = {
            "unique_id": selector.xpath('//span[@class="product-id__number"]/text()').get() or "",
            "competitor_name": "lidl",
            "store_name": "",
            "store_addressline1": "",
            "store_addressline2": "",
            "store_suburb": "",
            "store_state": "",
            "store_postcode": "",
            "store_addressid": "",
            "extraction_date": self.extraction_date,
            "product_name": selector.xpath('//h1[@class="heading__title"]/text()').get() or "",
            "brand": selector.xpath('//a[contains(@class, "heading__brand")]/text()').get() or "",
            "brand_type": "",
            "grammage_quantity": "",
            "grammage_unit": "",
            "drained_weight": "",
            "producthierarchy_level1": breadcrumb_levels[0] if len(breadcrumb_levels) > 0 else "",
            "producthierarchy_level2": breadcrumb_levels[1] if len(breadcrumb_levels) > 1 else "",
            "producthierarchy_level3": breadcrumb_levels[2] if len(breadcrumb_levels) > 2 else "",
            "producthierarchy_level4": breadcrumb_levels[3] if len(breadcrumb_levels) > 3 else "",
            "producthierarchy_level5": breadcrumb_levels[4] if len(breadcrumb_levels) > 4 else "",
            "producthierarchy_level6": breadcrumb_levels[5] if len(breadcrumb_levels) > 5 else "",
            "producthierarchy_level7": breadcrumb_levels[6] if len(breadcrumb_levels) > 6 else "",
            "regular_price": selector.xpath('//div[@class="m-price__price"]/text()').get() or "",
            "selling_price": selector.xpath('//div[@class="m-price__price"]/text()').get() or "",
            "price_was": "",
            "promotion_price": "",
            "promotion_valid_from": "",
            "promotion_valid_upto": "",
            "promotion_type": "",
            "percentage_discount": "",
            "promotion_description": "",
            "package_sizeof_sellingprice": "",
            "per_unit_sizedescription": "",
            "price_valid_from": "",
            "price_per_unit": "",
            "multi_buy_item_count": "",
            "multi_buy_items_price_total": "",
            "currency": "EUR",
            "breadcrumb": breadcrumbs,  
            "pdp_url": product_url or "",
            "variants": "",
            "product_description": self.extract_description(selector) or "",
            "instructions": "",
            "storage_instructions": "",
            "preparationinstructions": "",
            "instructionforuse": "",
            "country_of_origin": "",
            "allergens": "",
            "age_of_the_product": "",
            "age_recommendations": "",
            "flavour": "",
            "nutritions": "",
            "nutritional_information": "",
            "vitamins": "",
            "labelling": "",
            "grade": "",
            "region": "",
            "packaging": "",
            "receipies": "",
            "processed_food": "",
            "barcode": "",
            "frozen": "",
            "chilled": "",
            "organictype": "",
            "cooking_part": "",
            "Handmade": "",
            "max_heating_temperature": "",
            "special_information": "",
            "label_information": "",
            "dimensions": "",
            "special_nutrition_purpose": "",
            "feeding_recommendation": "",
            "warranty": "",
            "color": "",
            "model_number": "",
            "material": "",
            "usp": "",
            "dosage_recommendation": "",
            "tasting_note": "",
            "food_preservation": "",
            "size": "",
            "rating": self.extract_rating(selector) or "",
            "review": self.extract_total_reviews(selector) or "",
            "file_name_1": f"{unique_id}_1.jpg" if len(image_urls) > 0 else "",
            "image_url_1": image_urls[0] if len(image_urls) > 0 else "",
            "file_name_2": f"{unique_id}_2.jpg" if len(image_urls) > 1 else "",
            "image_url_2": image_urls[1] if len(image_urls) > 1 else "",
            "file_name_3": f"{unique_id}_3.jpg" if len(image_urls) > 2 else "",
            "image_url_3": image_urls[2] if len(image_urls) > 2 else "",
            "competitor_product_key": "",
            "fit_guide": "",
            "occasion": "",
            "material_composition": "",
            "style": "",
            "care_instructions": "",
            "heel_type": "",
            "heel_height": "",
            "upc": unique_id,
            "features": "",
            "dietary_lifestyle": "",
            "manufacturer_address": "",
            "importer_address": "",
            "distributor_address": "",
            "vinification_details": "",
            "recycling_information": "",
            "return_address": "",
            "alchol_by_volume": "",
            "beer_deg": "",
            "netcontent": "",
            "netweight": "",
            "site_shown_uom": "",
            "ingredients": "",
            "random_weight_flag": "",
            "instock": "",
            "promo_limit": "",
            "product_unique_key": "",
            "multibuy_items_pricesingle": "",
            "perfect_match": "",
            "servings_per_pack": "",
            "Warning": "",
            "suitable_for": "",
            "standard_drinks": "",
            "environmental": "",
            "grape_variety": "",
            "retail_limit": "",
        }

        return self.product_data

    def extract_breadcrumbs(self, selector):
        """Extract and clean breadcrumbs."""
        breadcrumb_parts = selector.xpath('//ol[contains(@class, "m-breadcrumbs")]//span[@itemprop="name"]/text()').getall()
        breadcrumbs = " > ".join([part.strip() for part in breadcrumb_parts if part.strip()])
        breadcrumb_levels = breadcrumbs.split(" > ") if breadcrumbs else []

        return breadcrumbs, breadcrumb_levels  

    def extract_rating(self, selector):
        """Extract product rating value."""
        rating_text = selector.xpath('//span[contains(@class, "ods-rating__info")]/text()').get()
        return re.search(r"(\d+(\.\d+)?)", rating_text).group(1) if rating_text else "Not Found"

    def extract_total_reviews(self, selector):
        """Extract total number of reviews."""
        total_reviews_text = selector.xpath('//span[contains(@class, "ods-rating__info-total")]/text()').get()
        return re.search(r"\d+", total_reviews_text).group() if total_reviews_text else "Not Found"
    
    def extract_description(self, selector):
        """Extract and clean product description."""
        description_parts = selector.xpath('//div[contains(@class, "accordion-list-item__description")]//text()').getall()
        clean_description = " ".join([part.strip() for part in description_parts if part.strip()])
        clean_description = re.sub(r"[^\w\s.,-]", "", clean_description)
        return clean_description if clean_description else "Not Found"

    def extract_image_urls(self, selector):
        """Extract image URLs, filtering out placeholders."""
        image_urls = selector.css('img[data-src]::attr(data-src)').getall()
        image_urls += selector.css('img[src]:not([data-src])::attr(src)').getall()
        return [img for img in image_urls if "placeholder" not in img and img.startswith("https")]

    def save_to_mongo(self, product_data):
        """Insert extracted product data into MongoDB `products_final` collection."""
        if product_data:
            self.final_collection.insert_one(product_data)  
            logger.info(f"Saved product: {product_data.get('product_name', 'Unnamed Product')}")
            
    def run_all(self):
        """Run the scraper for all product URLs stored in MongoDB."""
        product_urls = self.fetch_product_urls()
        for url in product_urls:
            logger.info(f"Scraping product: {url}")
            selector = self.fetch_page(url)
            if selector:
                product_data = self.extract_product_data(selector, url)  
                if product_data: 
                    self.save_to_mongo(product_data) 
                    self.display_product_data()  

    def display_product_data(self):
        """Print extracted product data."""
        logger.info("Extracted Product Data:")
        for key, value in self.product_data.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    scraper = LidlScraper("mongodb://localhost:27017/")
    scraper.run_all()