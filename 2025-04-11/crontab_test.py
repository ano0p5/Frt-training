
from curl_cffi import requests
from pymongo import MongoClient

class AdvisorScraper:
    def __init__(self):
        self.base_url = "https://eva-personnel-service.evipscloud.com/advisors"
        self.limit = 18
        self.offset = 0
        self.total_count = 0
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

        
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["crontab"]
        self.collection = self.db["test"]

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

            listings = []
            for record in records:
                self.total_count += 1  

                name_data = record.get("name", "")
                if isinstance(name_data, dict):
                    first_name = name_data.get("firstName", "")
                    last_name = name_data.get("lastName", "")
                else:
                    first_name = name_data
                    last_name = ""
                    
                
                accounts = record.get("accounts", [])
                office_name = ""
                associated_shops = []
                if accounts:
                    associated_shops = accounts[0].get("associatedShops", [])
                    if associated_shops:
                        office_name = associated_shops[0].get("name", "")

               
                title = accounts[0].get("title", "") if accounts else ""
                description = accounts[0].get("evTitle", "") if accounts else ""

               
                languages = ", ".join(accounts[0].get("languages", [])) if accounts else ""

                
                profile_picture = record.get("profilePicture", "")
                profile_thumbnail = record.get("profileThumbnail", "")
                logo_picture = record.get("logoPicture", "")
                image_url = ", ".join(filter(None, [profile_picture, profile_thumbnail, logo_picture]))

                
                contact = accounts[0].get("contact", {}) if accounts else {}
                email_ = ", ".join(filter(None, [contact.get("email", ""), contact.get("alternativeEmail", "")]))
                website = contact.get("website", "")

                
                phone_numbers = accounts[0].get("phoneNumbers", []) if accounts else []
                office_phone_numbers = ", ".join([pn.get("phone", "") for pn in phone_numbers if pn.get("type") == "office"])
                agent_phone_numbers = ", ".join([pn.get("phone", "") for pn in phone_numbers if pn.get("type") == "cell"])

                
                social_profiles = accounts[0].get("socialProfiles", []) if accounts else []
                social = ", ".join([f"{sp.get('type', '')}: {sp.get('url', '')}" for sp in social_profiles if isinstance(sp, dict)])

                
                associated_shop = associated_shops[0] if associated_shops else {}
                address = associated_shop.get("address", "")
                city = associated_shop.get("city", "")
                state = associated_shop.get("state", "")
                country = associated_shop.get("country", "")
                zipcode = associated_shop.get("postalCode", "")

                middle_name = ""               
               
                profile_url = website  

                listing = (
                    f"first_name: {first_name}\n"
                    f"middle_name: {middle_name}\n"
                    f"last_name: {last_name}\n"
                    f"office_name: {office_name}\n"
                    f"title: {title}\n"
                    f"description: {description}\n"
                    f"languages: {languages}\n"
                    f"image_url: {image_url}\n"
                    f"address: {address}\n"
                    f"city: {city}\n"
                    f"state: {state}\n"
                    f"country: {country}\n"
                    f"zipcode: {zipcode}\n"
                    f"office_phone_numbers: {office_phone_numbers}\n"
                    f"agent_phone_numbers: {agent_phone_numbers}\n"
                    f"email: {email_}\n"
                    f"website: {website}\n"
                    f"social: {social}\n"
                    f"profile_url: {profile_url}\n"
                    f"{'-' * 50}"
                )
                listings.append(listing)

                self.collection.insert_one({
                    "record_number": self.total_count,
                    "first_name": first_name,
                    "middle_name": middle_name,
                    "last_name": last_name,
                    "office_name": office_name,
                    "title": title,
                    "description": description,
                    "languages": languages,
                    "image_url": image_url,
                    "address": address,
                    "city": city,
                    "state": state,
                    "country": country,
                    "zipcode": zipcode,
                    "office_phone_numbers": office_phone_numbers,
                    "agent_phone_numbers": agent_phone_numbers,
                    "email": email_,
                    "website": website,
                    "social": social,
                    "profile_url": profile_url,
                })

            print("\n\n".join(listings))

            self.offset += self.limit

scraper = AdvisorScraper()
scraper.fetch_advisors()