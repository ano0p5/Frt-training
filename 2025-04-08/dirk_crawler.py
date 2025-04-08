import requests
from parsel import Selector

class DirkCategoryScraper:
    def __init__(self):
        self.start_url = 'https://www.dirk.nl/boodschappen'
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'cookie': 'experiments=%7B%22offers-departments-button%22%3A%22b%22%7D; noOrderMessageClosed=false; accepted=false; _ga=GA1.1.1701329248.1744087002; recallsClosed=%5B186249%2C186238%5D; cookies-banner-shown=true; popupShown=%7B%22id%22%3A168703%2C%22date%22%3A%222025-04-08T04%3A37%3A59.382Z%22%7D; _ga_C9C5TZDTZM=GS1.1.1744096036.2.1.1744096564.0.0.0',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://www.google.com/',
            'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
        }

    def fetch_page(self):
        print(f"Requesting: {self.start_url}")
        response = requests.get(self.start_url, headers=self.headers)
        print(f"Status Code: {response.status_code}")
        return response.text if response.status_code == 200 else None

    def extract_category_urls(self, html):
        selector = Selector(text=html)
        relative_links = selector.xpath("//article[@data-section='departments']//a/@href").getall()
        base_url = "https://www.dirk.nl"
        full_links = [base_url + link if not link.startswith(base_url) else link for link in relative_links]
        return full_links

    def run(self):
        html = self.fetch_page()
        if html:
            category_urls = self.extract_category_urls(html)
            print("\nFound category URLs:")
            for url in category_urls:
                print(url)
        else:
            print("Failed to fetch or parse the page.")

if __name__ == '__main__':
    DirkCategoryScraper().run()
