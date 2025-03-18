import requests
import pymongo
import json
from parsel import Selector
from urllib.parse import urljoin
from datetime import datetime
import logging

class Parser:
    def __init__(self):
        self.client = pymongo.MongoClient()
        self.db = self.client["Next_DB"]
        self.product_collection = self.db["parsed_data"]
        self.competitor_name = "next"
        self.extraction_date = datetime.now().strftime("%Y-%m-%d")
        self.base_url = "https://www.next.co.uk/"

    def get_response(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response
        except:
            return None
        
    def extract_structured_data(self, selector):
        structured_data = selector.xpath("//script[@type='application/ld+json']/text()").get()
        if structured_data:
            try:
                return json.loads(structured_data)
            except:
                return {}
        return {}

    def extract_breadcrumb_and_hierarchy(self, selector):
        next_data_script = selector.xpath("//script[@id='__NEXT_DATA__']/text()").get()

        if next_data_script:
            try:
                next_data = json.loads(next_data_script)

                data = next_data["props"]["pageProps"]["dehydratedState"]["queries"][1]["state"]["data"]
                gender = data.get("gender", "Unknown")
                category = data.get("category", "Unknown")
                collection = data.get("collection", "Unknown")

                body_fit = (
                    data.get("fitsAndColourways", {})
                    .get("fits", [{}])[0]
                    .get("displayText", "Unknown")
                )

                breadcrumb = f"Home > {gender} > {category} > {collection}"
                

                product_hierarchy = {
                    "producthierarchy_level1": "Home",
                    "producthierarchy_level2": gender,
                    "producthierarchy_level3": category,
                    "producthierarchy_level4": collection,
                    "body_fit" : body_fit
                }

                return breadcrumb, product_hierarchy

            except:
                return "", {}
        return "", {}


    def extract_sizes_and_availability(self, offers):
        sizes = []
        for offer in offers:
            size = offer.get("name", "").strip()
            if size:
                sizes.append(size)
        return sizes

        
    def variant_colors(self, selector):
        next_data_script = selector.xpath("//script[@id='__NEXT_DATA__']/text()").get()

        if next_data_script:
            try:
                next_data = json.loads(next_data_script)
                colourways = next_data["props"]["pageProps"]["dehydratedState"]["queries"][1]["state"]["data"].get("fitsAndColourways", {}).get("colourways", {}).get("colourways", [])
                colors = [colourway.get("displayText", "").strip() for colourway in colourways if colourway.get("displayText")]
                if colors:
                    return colors
            except:
                return []

    
    def extract_ratings_and_reviews(self, product_data):
        rating = product_data.get("aggregateRating", {}).get("ratingValue", "")
        review_count = product_data.get("aggregateRating", {}).get("reviewCount", "")

        if not rating or not review_count:
            rating_summary = product_data.get("reviews", {}).get("ratingSummary", {})
            rating = rating_summary.get("overallRating", "")
            review_count = rating_summary.get("totalReviewCount", "")

        reviews = product_data.get("reviews", {}).get("reviews", [])
        if not reviews:
            reviews = product_data.get("review", [])

        extracted_reviews = []
        for review in reviews:
            content = review.get("description", "").strip()
            if content:
                extracted_reviews.append(content)

        joined_reviews = ".".join(extracted_reviews).strip()

        return rating, review_count, joined_reviews

    def extract_colors(self, selector):
        color = selector.xpath("//button[@role='button']/img/@alt").get()
        return color if color else ""
    
    def parse_product(self, url):
        response = self.get_response(url)
        if not response:
            return

        selector = Selector(response.text)

        product_data = self.extract_structured_data(selector)

        breadcrumb, product_hierarchy  = self.extract_breadcrumb_and_hierarchy(selector)
        

        product_name = product_data.get("name", "")
        brand = product_data.get("brand", {}).get("name", "")
        model_number = product_data.get("sku", "").replace("-", "")
        currency = "pounds"
        regular_price = product_data.get("offers", [{}])[0].get("price", "")
        image_urls = selector.xpath("//div[@data-testid='pdp-thumbs']//img/@src").getall()
        image_urls = [urljoin(self.base_url, img) for img in image_urls]

        image_data = {}
        for idx, img_url in enumerate(image_urls):
            image_data[f"image_url_{idx + 1}"] = img_url

        
        product_description = " ".join(selector.xpath("//div[@data-testid='item-description-tone-of-voice']//text()").getall()).strip()

        variant_colors = self.variant_colors(selector)


        material = selector.xpath("//p[@data-testid='item-description-composition']//text()").get()
        instructions = selector.xpath("//p[@data-testid='item-description-washing-instructions']//text()").get()

        rating, review_count, extracted_reviews = self.extract_ratings_and_reviews(product_data)

        color = self.extract_colors(selector)

        product_data = {
            "unique_id": model_number.replace("-", ""),  
            "competitor_name": self.competitor_name,
            "extraction_date": self.extraction_date,
            "product_name": product_name,
            "brand": brand,
            "producthierarchy_level1": product_hierarchy.get("producthierarchy_level1", ""),
            "producthierarchy_level2": product_hierarchy.get("producthierarchy_level2", ""),
            "producthierarchy_level3": product_hierarchy.get("producthierarchy_level3", ""),
            "producthierarchy_level4": product_hierarchy.get("producthierarchy_level4", ""),
            "producthierarchy_level5": "",  
            "regular_price": regular_price,
            "selling_price": regular_price,  
            "promotion_price": "",  
            "promotion_valid_from": "",  
            "promotion_valid_upto": "", 
            "promotion_type": "",  
            "promotion_description": "", 
            "currency": currency,
            "breadcrumb": breadcrumb,
            "pdp_url": url,
            "variant_size":self.extract_sizes_and_availability(product_data.get("offers", [])), 
            "product_description": product_description,
            "country_of_origin": "uk",  
            "instructions": instructions,
            "color": color,
            "model_number": model_number.replace("-", ""),  # Fixing model number format
            "material": material,
            "size": "", 
            "rating": rating,
            "review": extracted_reviews,
            "image_url_1": image_data.get("image_url_1", ""),
            "image_url_2": image_data.get("image_url_2", ""),
            "image_url_3": image_data.get("image_url_3", ""),
            "competitor_product_key": "",  
            "fit_guide": "", 
            "occasion": product_hierarchy.get("producthierarchy_level4", ""), 
            "material_composition": material,  
            "style": "", 
            "care_instructions": instructions,  
            "upc": "",  
            "features": "", 
            "gender": product_hierarchy.get("producthierarchy_level2", ""),
            "clothing_type": material,  
            "clothing_fit": "",  
            "clothing_length": "", 
            "collar_type": "",  
            "pattern": "", 
            "pocket": "", 
            "fastener_closure_type": "", 
            "rise_pants_capris": "",  
            "pant_leg_cut": "",  
            "iron": "",  
            "stretch": "",  
            "maternity": "", 
            "thermal": "",  
            "clothing_weight": "",  
            "upper_body_strap_configuration": "",  
            "clothing_leg_bottom_opening_style": "",  
            "cuffs_style": "", 
            "neck_style": "",  
            "clothing_length_style": "", 
            "sleeve_length_style": "", 
            "ean": "",  
            "body_fit":product_hierarchy.get("body_fit","") , 
            "variant_color": variant_colors, 
            "social_proof_label": "", 
            "stock_availability": "yes",  
        }
        
        self.product_collection.insert_one(product_data)

if __name__ == "__main__":
    parser = Parser()

    client = pymongo.MongoClient()
    db = client["Next_DB"]
    product_collection = db["Product_urls"]

    product_urls = product_collection.find_one().get("urls", [])

    for product_url in product_urls:
        logging.info(f"Parsing product URL: {product_url}")
        parser.parse_product(product_url)
