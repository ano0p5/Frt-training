import json
from curl_cffi import requests

class AdvisorScraper:
    def __init__(self):
        self.base_url = "https://eva-personnel-service.evipscloud.com/advisors"
        self.limit = 18
        self.offset = 0
        self.headers = {
            "authority": "eva-personnel-service.evipscloud.com",
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "origin": "https://www.evrealestate.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://www.evrealestate.com/",
            "sec-ch-ua": '"Chromium";v="101", "Google Chrome";v="101", "Not A;Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
        }

    def fetch_advisors(self):
        while True:
            params = {
                "sortKey": "firstname",
                "sortDir": "asc",
                "offset": str(self.offset),
                "limit": str(self.limit)
            }

            response = requests.get(self.base_url, headers=self.headers, params=params)
            data = response.json()
            print(json.dumps(data, indent=2))

            if not data.get("records"):
                print("No more advisors found.")
                break

            self.offset += self.limit

scraper = AdvisorScraper()
scraper.fetch_advisors()
