from pathlib import Path
import logging
import json
import pandas as pd  # type: ignore
from pandas import DataFrame

# Variables
global_variables: dict = {"root_path": None}

# Initalize base logic for the libary
logger = logging.getLogger(__name__)
global_variables["root_path"] = Path(__file__).parent.parent
logger.debug(
    f"Root path set to {global_variables['root_path']}. This is the path to the root of the project."
)


# MARK: Functions
def load_text_json(*, language: str, interface: str, filename: str) -> dict:
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
        file_path = (
            Path(global_variables["root_path"]) / "resources" / f"{filename}.json"
        )
        with open(file_path, "r", encoding="utf-8") as file:
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
        file_path = global_variables["root_path"] / "resources" / "settings.json"
        with open(file_path, "r", encoding="utf-8") as file:
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


def save_dataframe_to_csv(df: DataFrame, filename: str) -> None:
    """
    Save a DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        filename (str): The name of the file to save the DataFrame to.
    """
    try:
        file_path = (
            global_variables["root_path"] / "data" / "output" / f"{filename}.csv"
        )
        df.to_csv(file_path, index=False)
        logger.info(f"DataFrame saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving DataFrame to CSV: {e}")

def calculate_monthly_payment_from_duration(
    target_amount: float, annual_interest_rate: float, duration_months: int
) -> float:
    """
    Calculate monthly payment for loans/savings using the annuity formula.
    Works for both savings goals and loan repayments.

    Args:
        target_amount: Total loan amount or savings goal.
        annual_interest_rate (float): Annual interest rate (e.g., 5 for 5%).
        duration_months (int): Loan term in months.

    Returns:
        float: Monthly payment amount.
    
    Raises:
        ValueError: If duration or rate is invalid.
    """
    if duration_months <= 0:
        raise ValueError("Duration must be positive.")
    if annual_interest_rate < 0:
        raise ValueError("Interest rate cannot be negative.")

    monthly_interest_rate = (
        annual_interest_rate / 100 / 12
    )  # Convert % to decimal and annual to monthly
    numerator = monthly_interest_rate * (1 + monthly_interest_rate) ** duration_months
    denominator = (1 + monthly_interest_rate) ** duration_months - 1
    monthly_payment = target_amount * (numerator / denominator)

    return round(monthly_payment, 2)  # Round to 2 decimal places (cents)