import json
import os

class Config:
    def __init__(self, config_file="config/settings.json"):
        self.settings = {
            "window": {
                "width": 1280,
                "height": 720,
                "title": "ChronoStorm Engine",
                "fps": 60
            },
            "debug": True
        }
        self.load(config_file)

    def load(self, config_file):
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_settings = json.load(f)
                    self.settings.update(user_settings)
            except Exception as e:
                print(f"Warning: Failed to load config, using defaults. Error: {e}")

game_config = Config()