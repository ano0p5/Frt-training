import json
import re

def validate_unwanted_chars(content, allowed_pattern=r"^[\x20-\x7E\n\r\t]+$"):
    """
    Checks if content contains only allowed printable ASCII characters.
    Logs unwanted characters with line numbers if found.
    """
    errors = []
    for i, line in enumerate(content.splitlines(), start=1):
        if not re.match(allowed_pattern, line):
            unwanted = set(char for char in line if not re.match(r"[\x20-\x7E\n\r\t]", char))
            errors.append(f"Line {i}: Unwanted characters found: {', '.join(map(repr, unwanted))}")
    return errors

def check_empty_quotes_in_json(data, path="root"):
    """Recursively checks JSON to ensure values are not incorrectly quoted."""
    errors = []
    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{path}.{key}"
            if isinstance(value, str) and (value.startswith("'") or value.startswith('"')) and (value.endswith("'") or value.endswith('"')):
                errors.append(f"{new_path}: Contains a quoted value: {value}")
            errors.extend(check_empty_quotes_in_json(value, new_path))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            new_path = f"{path}[{i}]"
            if isinstance(item, str) and (item.startswith("'") or item.startswith('"')) and (item.endswith("'") or item.endswith('"')):
                errors.append(f"{new_path}: Contains a quoted value: {item}")
            errors.extend(check_empty_quotes_in_json(item, new_path))
    return errors

def validate_json(file_path):
    """Validates JSON structure, checks for unwanted characters and incorrect quotes."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        char_errors = validate_unwanted_chars(content)
        
        data = json.loads(content)  # Parse JSON
        
        quote_errors = check_empty_quotes_in_json(data)
        
        errors = char_errors + quote_errors
        
        if errors:
            print(f"\n❌ Errors found in {file_path}:\n")
            for error in errors:
                print(error)
            return False
        else:
            print(f"\n✅ {file_path} is valid.")
            return True
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON format error in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error reading {file_path}: {e}")
        return False

if __name__ == "__main__":
    file_path = "/home/anoop/frt/2025-4-03/csv_json/json_validator/products.json"
    
    validate_json(file_path)
