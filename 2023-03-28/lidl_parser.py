import requests
import json
import re
from parsel import Selector
from pymongo import MongoClient
from datetime import datetime


client = MongoClient("mongodb://localhost:27017/")
db = client["lidl"]
product_collection = db["crawler"]  
parsed_data_collection = db["parsed_products"]  

def fetch_lidl_product_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None, None, None, None
    
    selector = Selector(response.text)
    json_data = extract_json_data(selector)
    breadcrumbs = extract_breadcrumbs(selector)
    description = extract_description(selector)
    grammage_quantity, fat_percentage, grammage_unit = extract_grammage_fat(selector)
    
    return json_data, breadcrumbs, description, grammage_quantity, fat_percentage, grammage_unit

def extract_json_data(selector):
    script_content = selector.css('script[type="application/ld+json"]::text').get()
    if script_content:
        try:
            return json.loads(script_content)
        except json.JSONDecodeError:
            return None
    return None

def extract_breadcrumbs(selector):
    """Extracts breadcrumbs and assigns them to hierarchy levels."""
    breadcrumbs = selector.xpath('//ol[contains(@class, "m-breadcrumbs")]//span[@itemprop="name"]/text()').getall()
    
    levels = [""] * 5
    for i, breadcrumb in enumerate(breadcrumbs[:5]):
        levels[i] = breadcrumb.strip()
    
    return levels

def extract_description(selector):
    """Extracts product description from the page."""
    description = selector.xpath('//div[contains(@class, "tab__content--description")]//text()').getall()
    return " ".join(desc.strip() for desc in description if desc.strip())

def extract_grammage_fat(selector):
    """Extracts grammage quantity, fat percentage, and grammage unit from description section."""
    description_text = extract_description(selector)

    fat_match = re.search(r"(\d+\.?\d*)%\s*fat", description_text, re.IGNORECASE)
    fat_percentage = fat_match.group(1) if fat_match else ""

    
    grammage_match = re.search(r"(\d+\.?\d*)\s*(ml|l|g|kg)", description_text, re.IGNORECASE)
    grammage_quantity = grammage_match.group(1) if grammage_match else ""
    grammage_unit = grammage_match.group(2) if grammage_match else ""

    return grammage_quantity, fat_percentage, grammage_unit

def parse_lidl_product(url):
    product_data, breadcrumb_levels, description, grammage_quantity, fat_percentage, grammage_unit = fetch_lidl_product_data(url)
    
    if not product_data:
        return {"error": "Failed to extract product data"}
    
    unique_id = str(product_data.get("sku", ""))
    images = product_data.get("image", [])
    
    parsed_data = {
        "unique_id": unique_id,
        "competitor_name": "Lidl",
        "extraction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "product_name": product_data.get("name", ""),
        "brand":"",
        "brand_type": "",
        "grammage_quantity": grammage_quantity,  
        "grammage_unit": grammage_unit,  
        "producthierarchy_level1": breadcrumb_levels[0],
        "producthierarchy_level2": breadcrumb_levels[1],
        "producthierarchy_level3": breadcrumb_levels[2],
        "producthierarchy_level4": breadcrumb_levels[3],
        "producthierarchy_level5": breadcrumb_levels[4],
        "regular_price": str(product_data.get("price", {}).get("referencePrice", "")),
        "selling_price": str(product_data.get("price", {}).get("finalPrice", "")),
        "price_was": "",
        "promotion_price": "",
        "promotion_valid_from": "",
        "promotion_valid_upto": "",
        "promotion_type": "",
        "percentage_discount": "",
        "promotion_description": "",
        "price_per_unit": str(product_data.get("price", {}).get("unitPrice", "")),
        "currency": product_data.get("price", {}).get("currency", ""),
        "breadcrumb": " > ".join(filter(None, breadcrumb_levels)),
        "pdp_url": url,
        "Fat %": fat_percentage, 
        "variants": "",
        "product_description": description,
        "instructions": "",
        "storage_instructions": "",
        "country_of_origin": "NL",
        "allergens": "",
        "nutritional_score": "",
        "organictype": "Organic" ,
    }
    
    for i, image_url in enumerate(images[:6]):
        parsed_data[f"file_name_{i+1}"] = f"{unique_id}_{i+1}.PNG"
        parsed_data[f"image_url_{i+1}"] = image_url

    parsed_data["upc"] = product_data.get("gtin", "")
    parsed_data["ingredients"] = ", ".join(product_data.get("ingredients", []))
    parsed_data["servings_per_pack"] = str(product_data.get("servingsPerPackage", ""))
    
    return parsed_data


product_urls = product_collection.find({}, {"product_url": 1, "_id": 0})  

for entry in product_urls:
    url = entry.get("product_url")
    if url:
        print(f"Processing: {url}")
        parsed_product = parse_lidl_product(url)
        
       
        parsed_data_collection.insert_one(parsed_product)
        print(f"Inserted product: {parsed_product.get('product_name')}")
