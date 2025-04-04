from pathlib import Path
import logging
import json

# Variables
global_variables: dict = {"root_path": None}

# Initalize base logic for the libary
logger = logging.getLogger(__name__)
global_variables['root_path'] = Path(__file__).parent.parent

#MARK: Functions
def load_text_json(*,language: str, interface: str, filename : str)-> dict:
    """
    Load text from a JSON file based on the specified language and interface.

    Args:
        language (str): The language code (e.g., "de", "en").
        interface (str): The name of the interface (e.g., "homescreen", "wealth_projection", "credit_simulation").
        filename (str): The name of the JSON file (without extension) to load the text from.

    Returns:
        dict: A dictionary containing the text for the specified interface in the proper language.
    """
    try:
        file_path = Path(global_variables["root_path"])/ "resources" / f"{filename}.json"
        with open(file_path, 'r', encoding='utf-8') as file:
            text = json.load(file)
        return text[language][interface]
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
    
def user_input_float(ui_text_input_request: str, ui_text_invalid_input: str) -> float:
    """
    Get a float input from the user with a prompt.

    Args:
        ui_text_input_request (str): The prompt text for user input.
        ui_text_invalid_input (str): The text to display when the user enters invalid input.

    Returns:
        float: The float value entered by the user.
    """
    while True:
        try:
            user_input = float(input(ui_text_input_request))
            return user_input
        except ValueError:
            print(ui_text_invalid_input)

def user_input_int(ui_text_input_request: str, ui_text_invalid_input: str) -> int:
    """
    Get an int input from the user with a prompt.

    Args:
        ui_text_input_request (str): The prompt text for user input.
        ui_text_invalid_input (str): The text to display when the user enters invalid input.

    Returns:
        int: The int value entered by the user.
    """
    while True:
        try:
            user_input = int(input(ui_text_input_request))
            return user_input
        except ValueError:
            print(ui_text_invalid_input)