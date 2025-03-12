import os
import requests
from pymongo import MongoClient

class ImageDownloader:
    def __init__(self, db_uri='mongodb://localhost:27017', db_name='reelly_db', collection_name='reelly_parser'):
        self.output_folder = 'soft_reely_images'
        os.makedirs(self.output_folder, exist_ok=True)

        self.field_prefixes = {
            'cover_image_url': 'cover',
            'architecture_images': 'architecture',
            'interior_images': 'interior',
            'lobby_images': 'lobby',
            'layout_images': 'layout'
        }

        # Create subfolders for each image type
        for prefix in self.field_prefixes.values():
            subfolder = os.path.join(self.output_folder, prefix)
            os.makedirs(subfolder, exist_ok=True)

        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.parser_collection = self.db[collection_name]

    def get_image_urls(self, doc):
        image_data = []
        project_id = doc.get("id", '')
        for field, prefix in self.field_prefixes.items():
            field_value = doc.get(field, "")
            if field_value:
                image_urls = [s.strip().strip('"') for s in field_value.split(',') if s.strip().strip('"')]
                for idx, url in enumerate(image_urls):
                    ext = self._get_file_extension(url)
                    if not ext:
                        print(f"Skipping {url} (no file extension)")
                        continue
                    filename = f"{project_id}_{prefix}_{idx + 1}{ext}" if len(image_urls) > 1 else f"{project_id}_{prefix}{ext}"
                    image_data.append((url, filename, prefix))
        return image_data

    def download_image(self, url, filename, prefix):
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                self.save_image(response, filename, prefix)
                print(f"Downloaded {url} to {prefix}/{filename}")
            else:
                print(f"Failed to download {url} (Status code: {response.status_code})")
        except Exception as e:
            print(f"Error downloading {url}: {e}")

    def save_image(self, response, filename, prefix):
        subfolder = os.path.join(self.output_folder, prefix)
        filepath = os.path.join(subfolder, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

    def _get_file_extension(self, url):
        return os.path.splitext(url)[1] or ""

    def start(self):
        for doc in self.parser_collection.find():
            image_data = self.get_image_urls(doc)
            for url, filename, prefix in image_data:
                self.download_image(url, filename, prefix)

    def close(self):
        self.client.close()

if __name__ == "__main__":
    downloader = ImageDownloader()
    downloader.start()
    downloader.close()

