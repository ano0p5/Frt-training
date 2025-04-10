import json
import re
import os
from pymongo import MongoClient


client = MongoClient("mongodb://localhost:27017/")
db = client["dirk"]
collection = db["products"]

file_paths = [
    "/home/anoop/frt/2025-04-10/biologisch-zuivel-kaas.html",
    "/home/anoop/frt/2025-04-10/eieren.html",
    "/home/anoop/frt/2025-04-10/kaas-gesneden.html",
    "/home/anoop/frt/2025-04-10/kaas-stuk.html",
    "/home/anoop/frt/2025-04-10/lactosevrije-zuivel.html",
    "/home/anoop/frt/2025-04-10/melk-karnemelk.html",
    "/home/anoop/frt/2025-04-10/overige-kazen.html",
    "/home/anoop/frt/2025-04-10/slagroom-kookroom.html",
    "/home/anoop/frt/2025-04-10/toetjes.html",
    "/home/anoop/frt/2025-04-10/vla.html",
    "/home/anoop/frt/2025-04-10/yoghurt-kwark-pap.html",
    "/home/anoop/frt/2025-04-10/zuiveldranken.html",
    "/home/anoop/frt/2025-04-10/boter-margarine.html"
]

for file_path in file_paths:
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        continue

    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    matches = re.findall(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
    if not matches:
        print(f"No JSON-LD found in: {file_path}")
        continue

    try:
        data = json.loads(matches[0])
        item_list = data["@graph"][0]["itemListElement"]

        for product in item_list:
            prod = product["item"]
            doc = {
                "name": prod.get("name", ""),
                "sku": str(prod.get("sku", "")),
                "image": prod.get("image", [""])[0] if isinstance(prod.get("image", ""), list) else "",
                "url": prod.get("url", ""),
                "source_file": os.path.basename(file_path)
            }
            collection.update_one(
                {"sku": doc["sku"]},
                {"$set": doc},
                upsert=True
            )

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")