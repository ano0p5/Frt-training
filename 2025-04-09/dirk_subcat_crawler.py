import requests

url = 'https://www.dirk.nl/boodschappen/zuivel-kaas/toetjes'

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'cookie': 'experiments=%7B%22offers-departments-button%22%3A%22b%22%7D; noOrderMessageClosed=false; _ga=GA1.1.1701329248.1744087002; recallsClosed=%5B186249%2C186238%5D; cookies-banner-shown=true; popupShown=%7B%22id%22%3A168703%2C%22date%22%3A%222025-04-08T04%3A37%3A59.382Z%22%7D; accepted=false; _ga_C9C5TZDTZM=GS1.1.1744199857.5.1.1744201467.0.0.0',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    'referer': 'https://www.dirk.nl/',  
    'origin': 'https://www.dirk.nl' 
}

session = requests.Session()

response = session.get(url, headers=headers)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    print("Request was successful!")
else:
    print(f"Request failed with status code: {response.status_code}")
