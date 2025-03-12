import requests
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["reelly_db"]
urls_collection = db["project_urls"]

search_url = "https://api.reelly.io/api:sk5LT7jx/projectsExternalSearch"
project_url_template = "https://api.reelly.io/api:sk5LT7jx/projects/{project_id}?user_id=36624"

headers = {
    "authorization": "Bearer eyJhbGciOiJBMjU2S1ciLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiemlwIjoiREVGIn0.gvg2X3Phs0YPNlsXXoJunoy5p36hi-Gj5t1jXhYpAFOLe2XyT3HRkZV5vGXVf0HP1PNIchO0BtqdsBtoBsiW8P01Dm0uA3o0.7CUTT8K2cP1_xZJCRh4_Ag.b7r4OZo5lsNNzGIKxwgtG5qzSQQtlDvv5xtC3Ktc4W77qt1S4L1E5ZUfKG9XzMzdiflMuS_a6pMDaE87aDD5Y-FWGp6y1AHeE-UnVe6Y9FsW7tHER6P8GM11bMplzV1uca9jn5MHE5ijipwnbsbtww.kbBVZ5mfbB7cf8xQLmYW4BC3ok-G8yIJOPvgdxKGK34",
    "origin": "https://soft.reelly.io",
    "referer": "https://soft.reelly.io/",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}

all_urls = [] 
for page in range(1, 62):
    response = requests.get(search_url, headers=headers, params={"page": page, "user_id": 36624})
    if response.status_code == 200:
        all_ids = [item["id"] for item in response.json().get("items", [])]
        all_urls.extend([project_url_template.format(project_id=pid) for pid in all_ids])
    else:
        break

urls_collection.insert_one({"project_urls": all_urls})

print(f"Total {len(all_urls)} URLs saved.")

