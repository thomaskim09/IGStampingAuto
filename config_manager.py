import json
import os

CONFIG_FILE = "config.json"


def save_config(config_data):
    """Saves the configuration dictionary to a JSON file."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")


def load_config():
    """Loads the configuration from a JSON file."""
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}
