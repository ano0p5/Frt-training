import requests
from pymongo import MongoClient
from parsel import Selector
import re


class MAndSCategoryScraper:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["m_and_s"]
        self.url_collection = self.db["category_urls"]
        self.facet_collection = self.db["facet_filters"]
        self.base_url = "https://www.marksandspencer.com"
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def fetch_category_urls(self):
        return self.url_collection.find({}, {"category_url": 1, "_id": 0})

    def follow_facet_url(self, facet_url, filter_value):
        try:
            response = requests.get(facet_url, headers=self.headers)
            if response.status_code == 200:
                selector = Selector(text=response.text)
                aria_label = selector.xpath(
                    f'//input[contains(@aria-label, "{filter_value}")]/@aria-label'
                ).get(default="")
                match = re.search(r"\((\d+)\)", aria_label)
                if match:
                    return int(match.group(1))
        except Exception:
            pass
        return 0

    def process_category(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            print(f"\nProcessing: {url}")

            if response.status_code == 200:
                selector = Selector(text=response.text)

                breadcrumb_items = selector.css('ul.breadcrumb_list___YAIM li a::text').getall()
                breadcrumb = " > ".join(breadcrumb_items)
                category_name = breadcrumb_items[-1] if breadcrumb_items else ""

                facet_links = selector.css('#facetUrls a')
                for link in facet_links:
                    href = link.attrib.get("href", "")
                    filter_value = link.css("::text").get(default="").strip()
                    filter_type = link.attrib.get("data-filter", "").strip()
                    full_url = self.base_url + href

                    count = self.follow_facet_url(full_url, filter_value)

                    facet_data = {
                        "url": full_url,
                        "category_url": url,
                        "breadcrumb": breadcrumb,
                        "category_name": category_name,
                        "count": count,
                        "filter_type": filter_type,
                        "filter_value": filter_value
                    }
                    for k, v in facet_data.items():
                        print(f"{k}: {v}")
                    print("-" * 60)

                    self.facet_collection.insert_one(facet_data)

        except Exception as e:
            print(f"Error processing {url}: {e}")

    def run(self):
        urls = self.fetch_category_urls()
        for url_data in urls:
            url = url_data["category_url"]
            self.process_category(url)


if __name__ == "__main__":
    scraper = MAndSCategoryScraper()
    scraper.run()
