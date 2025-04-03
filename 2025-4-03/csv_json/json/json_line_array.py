import json

def json_array_to_line_format(input_json, output_jsonl):
    with open(input_json, mode='r', encoding='utf-8') as file:
        data = json.load(file)
    
    with open(output_jsonl, mode='w', encoding='utf-8') as file:
        for entry in data:
            file.write(json.dumps(entry) + '\n')

def json_line_format_to_array(input_jsonl, output_json):
    with open(input_jsonl, mode='r', encoding='utf-8') as file:
        data = [json.loads(line) for line in file]
    
    with open(output_json, mode='w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


json_array_to_line_format('/home/anoop/frt/2025-4-03/csv_json/json/products.json', '/home/anoop/frt/2025-4-03/csv_json/json/output_line.jsonl')
json_line_format_to_array('/home/anoop/frt/2025-4-03/csv_json/json/output_line.jsonl', '/home/anoop/frt/2025-4-03/csv_json/json/output_array.json')
