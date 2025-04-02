from pathlib import Path
import logging
import json

# Variables
global_variables: dict = {"root_path": None}

# Initalize base logic for the libary
logger = logging.getLogger(__name__)
global_variables['root_path'] = Path(__file__).parent.parent

#MARK: Functions
def load_ui_text(*,language: str, interface: str)-> dict:
    """
    Load UI text from a JSON file based on the specified interface.

    Args:
        language (str): The language code (e.g., "de", "en").
        interface (str): The name of the interface (e.g., "homescreen","wealth_projection", "credit_simulation").

    Returns:
        dict: A dictionary containing the UI text for the specified interface in the proper language.
    """
    try:
        file_path = global_variables["root_path"]/"resources"/"ui_text.json"
        with open(file_path, 'r', encoding='utf-8') as file:
            ui_text = json.load(file)
        return ui_text[language][interface]
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from file: {file_path}")
        return {}
    
def load_settings() -> dict:
    """
    Load settings from a JSON file.

    Returns:
        dict: A dictionary containing the settings.
    """
    try:
        file_path = global_variables["root_path"]/"resources"/"settings.json"
        with open(file_path, 'r', encoding='utf-8') as file:
            settings = json.load(file)
        return settings
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from file: {file_path}")
        return {}