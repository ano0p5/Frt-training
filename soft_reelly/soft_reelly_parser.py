import pymongo
import requests
from datetime import datetime, timezone

class ProjectFetcher:
    def __init__(self, db_url, db_name, collection_name, project_data_collection, headers, payload):
        self.client = pymongo.MongoClient(db_url)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]  
        self.project_data_collection = self.db[project_data_collection]  
        
        self.headers = headers
        self.payload = payload

    def format_date(self, timestamp):
        return datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).strftime('%d-%b-%Y') if timestamp else None

    def fetch_total_units(self, project_id):
        url = f"https://api.reelly.io/api:sk5LT7jx/get-project-additional-info/{project_id}"
        response = requests.get(url, headers=self.headers, params=self.payload)
        
        if response.status_code == 200:
            data = response.json()
            total_units = sum(unit.get("Units_amount", 0) for unit in data.get('inventory', []))
            return total_units
        else:
            print(f"Failed to fetch total units for project {project_id}")
            return 0    

    def fetch_number_of_parking(self, project_id):
        api_url = f"https://xdil-qda0-zofk.m2.xano.io/api:sk5LT7jx/parkings?project_id={project_id}"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            
            return str(sum(unit.get("Parking_spaces", 0) or 0 for unit in data))
        else:
            print(f"Failed to fetch parking spaces for project {project_id}")
            return "0"

    def parse_project_data(self, data):
        project_id = str(data.get('id', ""))
        total_units = self.fetch_total_units(project_id)
        number_of_parking = self.fetch_number_of_parking(project_id)

        overview_text = data.get("Overview", "")
        if not isinstance(overview_text, str):
            overview_text = ""

        parsed_data = {
            "url": f"https://soft.reelly.io/project/general?projectid={project_id}&utm_source=reelly_platform",
            "id": project_id,
            "project_name": str(data.get("Project_name", "")),
            "area_name": str(data.get("Area_name", "")),
            "region": str(data.get("Region", "")),
            "completion_date": str(data.get("Completion_date", "")),
            "development_status": str(data.get("Status", "")),
            "coordinates": str(data.get("Coordinates", "")),
            "minimum_price": str(data.get("min_price", "")),

            "overview": " ".join(overview_text.replace("\n", " ").replace("#", "").split())
                        .replace("Project general facts ", "")
                        .replace("Finishing and materials ", "")
                        .replace("Kitchen and appliances ", "")
                        .replace("Furnishing ", "")
                        .replace("Location description and benefits ", ""),

            "units_types": ", ".join(str(item) for item in data.get("Units_types", []) if item),
            "sale_status": str(data.get("sale_status", "")),
            "completion_time": self.format_date(data.get("Completion_time")),
            "created_at": self.format_date(data.get("created_at")),
            "cover_image_url": str(data.get("cover", {}).get("url", "")),
            "last_modified": self.format_date(data.get("Last_Modified")),

            "developer_id": str(data.get("Developer", [{}])[0].get("id", "")) if isinstance(data.get("Developer"), list) else "",
            "developer_name": str(data.get("Developer", [{}])[0].get("Name", "")) if isinstance(data.get("Developer"), list) else "",
            "developer_website": str(data.get("Developer", [{}])[0].get("website", "")) if isinstance(data.get("Developer"), list) else "",

            "payment_plan": ", ".join(
                f"{str(payment.get('Percent_of_payment', '0'))}-{str(payment.get('Payment_time', '').strip())}"
                for sublist in data.get("Payment_plans", []) if isinstance(sublist, list)
                for payment in sublist if isinstance(payment, dict) and payment.get("Percent_of_payment") and payment.get("Payment_time")
            ),

            "facilities": ", ".join(
                str(facility.get("Name", "").strip().replace("\n", "").replace("\u0026", "&"))
                for sublist in data.get("Facilities", []) if isinstance(sublist, list)
                for facility in sublist if isinstance(facility, dict) and facility.get("Name")
            ),

            "map_points": ", ".join(
                f"{str(point.get('Point_name', ''))}-{str(point.get('Distance_km', ''))}"
                for sublist in data.get("Map_points", []) if isinstance(sublist, list)
                for point in sublist if isinstance(point, dict) and point.get("Point_name") and point.get("Distance_km") is not None
            ),

            "unit_bedrooms": ", ".join(
                f"{str(unit.get('unit_bedrooms', ''))} - {str(unit.get('Area_from_sqft', 'N/A'))} sqft - {str(unit.get('Area_to_sqft', 'N/A'))} sqft , AED {str(unit.get('Price_from_AED', 'None'))} - AED {str(unit.get('Price_to_AED', 'None'))}"
                for unit in data.get("Starting_price", []) if isinstance(unit, dict) and unit.get("unit_bedrooms")
            ),

            "architecture_images": ", ".join(
                str(img.get("url", "")) for img in (data.get("Architecture") or []) if isinstance(img, dict) and img.get("url")
            ),
            "interior_images": ", ".join(
                str(img.get("url", "")) for img in (data.get("Interior") or []) if isinstance(img, dict) and img.get("url")
            ),
            "lobby_images": ", ".join(
                str(img.get("url", "")) for img in (data.get("Lobby") or []) if isinstance(img, dict) and img.get("url")
            ),
            "layout_images": ", ".join(
                str(img.get("url", "")) for img in (data.get("Layouts_preview_img") or []) if isinstance(img, dict) and img.get("url")
            ),


            "service_charge": str(data.get("Service_Charge", "")),
            "floors": str(data.get("Floors", "")),
            "furnishing": str(data.get("Furnishing", "")),

        "developer_logo": str(next(
            (dev.get("Logo_image", [{}])[0].get("url", "") for dev in data.get("Developer", []) 
            if isinstance(dev, dict) and isinstance(dev.get("Logo_image"), list) and len(dev.get("Logo_image")) > 0),
            ""
        )),

        "floor_plans_pdf": ", ".join(
            str(plan.get("url", "")) for plan in data.get("Units_layouts_PDF", []) if isinstance(plan, dict) and plan.get("url")
        ),


        
            "marketing_brochure": data.get("Brochure") ,
            "total_units": str(total_units),
            "number_of_parking": str(number_of_parking),
        }

        return parsed_data


    def save_to_mongo(self, data):
        try:
            self.project_data_collection.insert_one(data)
            print("Data inserted into MongoDB successfully")
        except Exception as e:
            print(f"Error inserting data into MongoDB: {e}")

    def fetch_data_from_url(self, url):
        response = requests.get(url, headers=self.headers, params=self.payload)
        
        if response.status_code == 200:
            data = response.json()
            parsed_data = self.parse_project_data(data)
            self.save_to_mongo(parsed_data)  
            print(parsed_data)
            return parsed_data
        else:
            print(f"Failed to fetch data from {url}")
            return None

    def get_project_data(self):
        project_data = self.collection.find({}, {"project_urls": 1})
        for project in project_data:
            for url in project["project_urls"]:
                self.fetch_data_from_url(url)

def main():
    headers = {
        "origin": "https://soft.reelly.io",
        "referer": "https://soft.reelly.io/",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }

    payload = {
        "user_id": "36624"
    }

    project_fetcher = ProjectFetcher(
        db_url="mongodb://localhost:27017/",
        db_name="reelly_db",
        collection_name="project_urls",
        project_data_collection="reelly_parser",  
        headers=headers,
        payload=payload
    )

    project_fetcher.get_project_data()

if __name__ == "__main__":
    main()



