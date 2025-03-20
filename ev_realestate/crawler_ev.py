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

            records = data.get("records", [])
            if not records:
                print("No more advisors found.")
                break

            for record in records:
                name = record.get("name", "")
                team_picture = record.get("teamPicture", "")
                logo_picture = record.get("logoPicture", "")
                contact = record.get("contact", {})
                email = contact.get("email", "")
                phone = contact.get("phone", "")
                website = contact.get("website", "")
                address = contact.get("address", "")
                address2 = contact.get("address2", "")
                city = contact.get("city", "")
                state = contact.get("state", "")
                postal_code = contact.get("postalCode", "")
                country = contact.get("country", "")
                languages = ", ".join(record.get("languages", []))
                bio = ", ".join([b.get("value", "") for b in record.get("bio", [])])
                associated_shops = record.get("associatedShops", [])

                print(f"Name: {name}")
                print(f"Team Picture: {team_picture}")
                print(f"Logo Picture: {logo_picture}")
                print(f"Email: {email}")
                print(f"Phone: {phone}")
                print(f"Website: {website}")
                print(f"Address: {address} {address2}")
                print(f"City: {city}")
                print(f"State: {state}")
                print(f"Postal Code: {postal_code}")
                print(f"Country: {country}")
                print(f"Languages: {languages}")
                print(f"Bio: {bio}")

                for shop in associated_shops:
                    shop_name = shop.get("name", "")
                    legal_name = shop.get("legalName", "")
                    location_name = shop.get("locationName", "")
                    shop_address = shop.get("address", "")
                    shop_city = shop.get("city", "")
                    shop_state = shop.get("state", "")
                    shop_postal_code = shop.get("postalCode", "")
                    shop_country = shop.get("country", "")
                    shop_domain = shop.get("domain", "")

                    print(f"Shop Name: {shop_name}")
                    print(f"Legal Name: {legal_name}")
                    print(f"Location Name: {location_name}")
                    print(f"Shop Address: {shop_address}")
                    print(f"Shop City: {shop_city}")
                    print(f"Shop State: {shop_state}")
                    print(f"Shop Postal Code: {shop_postal_code}")
                    print(f"Shop Country: {shop_country}")
                    print(f"Shop Domain: {shop_domain}")
                
                print("-" * 50)

            self.offset += self.limit

scraper = AdvisorScraper()
scraper.fetch_advisors()
