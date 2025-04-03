import csv
import re

def validate_unwanted_chars(line, line_number, allowed_pattern=r"^[\x20-\x7E\n\r\t]+$"):
    """
    Checks if a line contains only allowed printable ASCII characters.
    Returns an error message if unwanted characters are found.
    """
    if not re.match(allowed_pattern, line):
        unwanted = set(char for char in line if not re.match(r"[\x20-\x7E\n\r\t]", char))
        return f"Line {line_number}: Unwanted characters found: {', '.join(map(repr, unwanted))}"
    return None

def validate_csv(file_path):
    """Validates CSV structure, checks for unwanted characters and missing values."""
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            
            if headers is None:
                print(f"\n❌ Error: {file_path} is empty or has no headers.")
                return False
            
            for line_number, row in enumerate(reader, start=2):  # Start from line 2 (after headers)
                line_content = ",".join(row)
                
                # Check for unwanted characters
                char_error = validate_unwanted_chars(line_content, line_number)
                if char_error:
                    errors.append(char_error)
                
                # Check for missing values
                for col_index, value in enumerate(row):
                    if value.strip() == "":
                        errors.append(f"Line {line_number}, Column {col_index+1}: Missing value")
        
        if errors:
            print(f"\n❌ Errors found in {file_path}:\n")
            for error in errors:
                print(error)
            return False
        else:
            print(f"\n✅ {file_path} is valid.")
            return True
    
    except Exception as e:
        print(f"\n❌ Error reading {file_path}: {e}")
        return False

if __name__ == "__main__":
    file_path = "/home/anoop/frt/2025-4-03/csv_json/json_validator/products.csv"
    
    validate_csv(file_path)
