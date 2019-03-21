import json

class Config:
    def __init__(self):
        self._load()
    def _load(self):
        with open('config.json', 'r') as f:
            for key, val in json.load(f).items():
                setattr(self, key, val)

config = Config()


