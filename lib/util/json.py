import json

def load_json(path: str):
    with open(path, 'r') as f:
        return json.load(f)


def write_json(obj, path: str):
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)
