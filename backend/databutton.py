import os
import json

class Secrets:
    def get(self, key):
        return os.environ.get(key)

class TextStorage:
    def get(self, key, default=None):
        # Implement simple local file storage for persistence
        try:
            with open(f".db_storage_{key}.txt", "r") as f:
                return f.read()
        except FileNotFoundError:
            return default

    def put(self, key, value):
        with open(f".db_storage_{key}.txt", "w") as f:
            f.write(value)

class JsonStorage:
    def put(self, key, value):
        with open(f".db_storage_{key}.json", "w") as f:
            json.dump(value, f)
    
    def get(self, key, default=None):
        try:
            with open(f".db_storage_{key}.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return default

class Storage:
    def __init__(self):
        self.text = TextStorage()
        self.json = JsonStorage()

secrets = Secrets()
storage = Storage()
