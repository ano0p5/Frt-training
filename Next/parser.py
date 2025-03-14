import requests
import logging
import re
from parsel import Selector
from urllib.parse import urljoin
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')

class Parser:
    def __init__(self):
        self.competitor_name = "Next"
        self.extraction_date = datetime.now().strftime("%Y-%m-%d")
        self.base_url = "https://www.next.co.uk/"

    def get_response(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logging.error(f"Error fetching URL {url}: {e}")
            return None

    def extract_sizes_and_availability(self, selector):
        sizes = []
        size_elements = selector.xpath("//script[@type='application/ld+json']/text()").get()
        if size_elements:
            try:
                import json
                product_data = json.loads(size_elements)
                if "offers" in product_data:
                    for offer in product_data["offers"]:
                        size = offer.get("name", "").strip()
                        availability = offer.get("availability", "").split("/")[-1]
                        sizes.append({"size": size, "availability": availability})
            except json.JSONDecodeError as e:
                logging.error(f"Error parsing JSON data: {e}")
        return sizes

    def parse_product(self, url):
        response = self.get_response(url)
        if not response:
            return

        selector = Selector(response.text)

        # Extract product information
        product_name = selector.xpath("//h1[@data-testid='product-title']/text()").get()
        price = selector.xpath("//span[@data-testid='product-price']/text()").get()
        regular_price = re.sub(r"[^\d.]", "", price) if price else ""
        product_image = selector.xpath("//meta[@property='og:image']/@content").get()
        image_urls = selector.xpath("//div[@data-testid='pdp-thumbs']//img/@src").getall()
        image_urls = [urljoin(self.base_url, img) for img in image_urls]

        breadcrumb = selector.xpath("//nav[@aria-label='breadcrumb']//a/text()").getall()

        # Extract description and other product details
        product_description = selector.xpath("//div[@class='description']//p//text()").get()
        instructions = selector.xpath("//p[@data-testid='item-description-washing-instructions']//text()").get()
        color = selector.xpath("//span[@data-testid='selected-colour-label']//text()").get()
        material = selector.xpath("//p[@data-testid='item-description-composition']//text()").get()
        model_number = selector.xpath("//span[@data-testid='product-code']//text()").get()
        rating = selector.xpath("//h3[contains(@class, 'MuiTypography-subtitle1')]/text()").get()
        rating = rating.split(" / ")[0].strip() if rating else ""
        reviews = selector.xpath("//p[contains(@class, 'MuiTypography-body1')]/text()").getall()
        reviews = [review.strip() for review in reviews if review.strip()]

        # Extract sizes and availability
        sizes = self.extract_sizes_and_availability(selector)

        # Product hierarchy
        product_hierarchy = {
            "producthierarchy_level1": breadcrumb[0] if len(breadcrumb) > 0 else "",
            "producthierarchy_level2": breadcrumb[1] if len(breadcrumb) > 1 else "",
            "producthierarchy_level3": breadcrumb[2] if len(breadcrumb) > 2 else "",
            "producthierarchy_level4": breadcrumb[3] if len(breadcrumb) > 3 else "",
            "producthierarchy_level5": breadcrumb[4] if len(breadcrumb) > 4 else "",
        }

        # Product Data
        product_data = {
            "unique_id": model_number,
            "product_name": product_name,
            "pdp_url": url,
            "image_urls": image_urls,
            "image": product_image,
            "competitor_name": self.competitor_name,
            "extraction_date": self.extraction_date,
            "regular_price": regular_price,
            "selling_price": regular_price,
            "promotion_price": "",  # Not handled yet
            "promotion_valid_from": "",  # Not handled yet
            "promotion_valid_upto": "",  # Not handled yet
            "promotion_type": "",  # Not handled yet
            "promotion_description": "",  # Not handled yet
            "currency": "GBP",
            "breadcrumb": breadcrumb,
            "product_description": product_description,
            "instructions": instructions,
            "color": color,
            "country_of_origin": "UK",
            "variants": sizes,
            "model_number": model_number,
            "material": material,
            "sizes": sizes,
            "rating": rating,
            "reviews": reviews,
            **product_hierarchy
        }

        # Print the product data on the terminal
        print("\nExtracted Product Data:")
        for key, value in product_data.items():
            print(f"{key}: {value}")
        print("\nProduct data extraction complete.\n")

if __name__ == "__main__":
    parser = Parser()
    test_url = "https://www.next.co.uk/style/su493564/ak3912" 
    parser.parse_product(test_url)
