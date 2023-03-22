import json

def load_json(path: str):
    """Retrieve the contents of a JSON file"""
    with open(path, 'r', encoding='utf-8') as source:
        return json.load(source)


def write_json(obj, path: str):
    """Write an object to a JSON file"""
    with open(path, 'w', encoding='utf-8') as destination:
        json.dump(obj, destination, indent=2)
