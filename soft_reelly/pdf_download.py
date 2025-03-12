import os
import re
import requests
from pymongo import MongoClient


def setup_download_folder(folder_name="soft_reelly_pdf"):
    os.makedirs(folder_name, exist_ok=True)
    return folder_name


def connect_to_mongo(db_name='reelly_db', collection_name='reelly_parser'):
    client = MongoClient('mongodb://localhost:27017')
    db = client[db_name]
    collection = db[collection_name]
    print("MongoDB connection established.")
    return client, collection


def download_pdf(url, file_path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded: {file_path}")
        else:
            print(f"Failed to download from {url} (status code: {response.status_code})")
    except Exception as e:
        print(f"Error downloading from {url}: {e}")


def get_drive_download_url(url):
    match = re.search(r"/d/([^/]+)/", url)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    print(f"Invalid Google Drive URL: {url}")
    return None


def process_pdf_url(url, file_path):
    if ".pdf" in url.lower():
        download_pdf(url, file_path)
    elif "https://drive.google.com" in url:
        download_url = get_drive_download_url(url)
        if download_url:
            download_pdf(download_url, file_path)
    else:
        print(f"Skipping unsupported URL: {url}")


def download_documents(doc_id, urls, prefix, download_folder):
    if isinstance(urls, str):
        urls = [urls]

    for idx, url in enumerate(urls):
        filename = f"{doc_id}_{prefix}_{idx + 1}.pdf" if len(urls) > 1 else f"{doc_id}_{prefix}.pdf"
        file_path = os.path.join(download_folder, filename)
        process_pdf_url(url, file_path)


def process_documents(collection, download_folder):
    for doc in collection.find():
        doc_id = str(doc.get("id") or doc.get("_id"))

        floor_urls = doc.get("floor_plans_pdf")
        if floor_urls:
            download_documents(doc_id, floor_urls, "floorplan", download_folder)

        brochure_urls = doc.get("marketing_brochure")
        if brochure_urls:
            download_documents(doc_id, brochure_urls, "brochure", download_folder)


def main():
    download_folder = setup_download_folder()
    client, collection = connect_to_mongo()

    try:
        process_documents(collection, download_folder)
    finally:
        client.close()
        print("MongoDB connection closed.")

if __name__ == "__main__":
    main()
