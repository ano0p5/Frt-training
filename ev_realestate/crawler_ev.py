import requests
import json

url = "https://eva-personnel-service.evipscloud.com/advisors"
limit = 18  # Number of items per page
offset = 0  # Starting point

headers = {
    "origin": "https://www.evrealestate.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://www.evrealestate.com/",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133")',
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}

while True:
    params = {
        "sortKey": "firstname",
        "sortDir": "asc",
        "offset": str(offset),
        "limit": str(limit)
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        response.raise_for_status()

        try:
            data = response.json()
            print(f"Response JSON: {json.dumps(data, indent=4)}")  # Print the entire response

            if not data.get("records"):
                print("No data returned.")
                break

            for record in data.get("records", []):
                print("========== ADVISOR ==========")
                print(f"First Name: {record.get('first_name', '')}")
                print(f"Middle Name: {record.get('middle_name', '')}")
                print(f"Last Name: {record.get('last_name', '')}")
                print(f"Office Name: {record.get('office_name', '')}")
                print(f"Title: {record.get('title', '')}")
                print(f"Description: {record.get('description', '')}")
                print(f"Languages: {', '.join(record.get('languages', []))}")
                print(f"Image URL: {record.get('image_url', '')}")
                print(f"Address: {record.get('address', '')}")
                print(f"City: {record.get('city', '')}")
                print(f"State: {record.get('state', '')}")
                print(f"Country: {record.get('country', '')}")
                print(f"Zipcode: {record.get('zipcode', '')}")
                print(f"Office Phone Numbers: {', '.join(record.get('office_phone_numbers', []))}")
                print(f"Agent Phone Numbers: {', '.join(record.get('agent_phone_numbers', []))}")
                print(f"Email: {record.get('email', '')}")
                print(f"Website: {record.get('website', '')}")
                print(f"Social Profiles: {record.get('social', {})}")
                print(f"Profile URL: {record.get('profile_url', '')}")
                print("=============================")

            offset += limit

        except json.JSONDecodeError:
            print("Error decoding JSON response.")
            print(f"Raw Response: {response.text}")
            break

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        break
