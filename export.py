import pandas as pd
import json
import os
import pathlib
from datetime import datetime

def export_to_csv(data, filename=None):
    """
    Export data to a CSV file
    
    Args:
    data: List of dictionaries or dictionary to export
    filename: Optional filename, will generate timestamped filename if not provided

    Returns:
    path: Path to the exported file
    """

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"scrape_results_{timestamp}.csv"

    # Ensure filename has .csv extension
    if not filename.lower().endswith(".csv"):
        filename += ".csv"

    # Make sure data is in the right format (list of dictionaries)
    if isinstance(data, dict):
        # Single dictionary - convert to list with one item
        df = pd.DataFrame([data])
    else:
        # List of dictionaries
        df = pd.DataFrame(data)

    # Create 'exports' directory if it doesn't exist
    # Use absolute path and pathlib for cross-platform compatibility
    export_dir = pathlib.Path.cwd() / "exports"
    export_dir.mkdir(exist_ok=True)

    # Create full path using pathlib for cross-platform compatibility
    path = export_dir / filename

    # Export to CSV
    df.to_csv(path, index=False)
    return str(path)

def export_to_json(data, filename=None):
    """
    Export data to a JSON file.

    Args:
    data: Dictionary or list to export
    filename: Optional filename, will generate timestamped filename if not provided

    Returns:
    path: Path to the exported file
    """

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"scrape_results_{timestamp}.json"

    # Ensure filename has .json extension
    if not filename.lower().endswith(".json"):
        filename += ".json"

    # Create 'exports' directory if it doesn't exist
    # Use absolute path and pathlib for cross-platform compatibility
    export_dir = pathlib.Path.cwd() / "exports"
    export_dir.mkdir(exist_ok=True)

    # Create full path using pathlib for cross-platform compatibility
    path = export_dir / filename

    # Export to JSON
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    return str(path)

def export_raw_text(text_data, filename=None):
    """
    Export raw text to a text file.
    
    Args:
    text_data: String to export
    filename: Optional filename, will generate timestamped filename if not provided
    
    Returns:
    path: Path to the exported file
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"raw_content_{timestamp}.txt"
    
    # Ensure filename has .txt extension
    if not filename.lower().endswith('.txt'):
        filename += '.txt'

    # Create 'exports' directory if it doesn't exist
    # Use absolute path and pathlib for cross-platform compatibility
    export_dir = pathlib.Path.cwd() / "exports"
    export_dir.mkdir(exist_ok=True)
    
    # Create full path using pathlib for cross-platform compatibility
    path = export_dir / filename
    
    # Export to text file
    with open(path, "w", encoding="utf-8") as f:
        f.write(text_data)
    
    return str(path)

def structure_parsed_data(parsed_result):
    """
    Attempts to structure the parsed text data into a dictionary or list of dictionaries.

    Args:
    parsed_result: String containing the parsed content

    Returns:
    structured_data: Dictionary or list of dictionaries with structured data
    """
    # Initial implementation - try to parse as JSON if it's already in that format
    try:
        # Check if the result is already valid JSON
        structured_data = json.loads(parsed_result)
        return structured_data
    except:
        pass

    # If it's not valid JSON, try to convert simple key-value text into a dictionary
    structured_data = {}
    lines = parsed_result.split("\n")

    for line in lines:
        line = line.strip()
        if ":" in line:
            key, value = line.split(":", 1)
            structured_data[key.strip()] = value.strip()

    return structured_data