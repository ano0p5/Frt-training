import csv
import json

def csv_to_json(csv_file, json_file):
    with open(csv_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        data = [row for row in csv_reader]
    
    with open(json_file, mode='w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def json_to_csv(json_file, csv_file):
    with open(json_file, mode='r', encoding='utf-8') as file:
        data = json.load(file)
    
    if data:
        keys = data[0].keys()
        with open(csv_file, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)


csv_to_json('/home/anoop/frt/2025-4-03/csv_json/input.csv', '/home/anoop/frt/2025-4-03/csv_json/output.json')
json_to_csv('/home/anoop/frt/2025-4-03/csv_json/output.json', '/home/anoop/frt/2025-4-03/csv_json/output.csv')
