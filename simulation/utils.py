from pathlib import Path
import logging
import json
import pandas as pd  # type: ignore
from pandas import DataFrame
import time
import sys
import os
import ctypes

# Variables
global_variables: dict = {
    "root_path": None,
    "user_data_root_path": Path.home() / "Desktop" / "Philanzen-Data",
}

# Initialize base logic for the library
logger = logging.getLogger(__name__)

# Sets up the root path based on whether the script is frozen or not.
if getattr(sys, "frozen", False):
    # The script runs as a frozen executable (.exe)
    # sys.executable is the path to the executable
    root_path = Path(sys.executable).parent
    logger.debug(f"Root path (frozen) set to {root_path}.")
else:
    # The script runs as a normal Python script
    root_path = Path(__file__).parent.parent
    logger.debug(
        f"Root path (not frozen) set to {root_path}. This is the path to the root of the project."
    )

global_variables["root_path"] = root_path
logger.debug(
    f"Root path set to {global_variables['root_path']}. This is the path to the root of the project."
)


# MARK: Functions
def setup_output_directory() -> None:
    """
    Sets up the output file directory structure and configures a custom folder icon.
    This function performs the following tasks:
    1. Creates the necessary directory structure for user data, including "data" and "logs" folders.
    2. Checks if the `desktop.ini` file exists in the user data root path to determine if the project structure is already set up.
    3. If the `desktop.ini` file does not exist:
        - Verifies the existence of the folder icon file.
        - Writes the `desktop.ini` file to configure the folder icon.
        - Hides the `desktop.ini` file from the user.
        - Forces Windows Explorer to reload the folder icon.
    Logs appropriate messages during each step of the process.
    Returns:
        None
    """

    # Create the output directory for user data if it does not exist.
    structure: dict[str, list] = {"data": [], "logs": []}

    for folder, subfolders in structure.items():
        (global_variables["user_data_root_path"] / folder).mkdir(
            parents=True, exist_ok=True
        )
        for sub in subfolders:
            (global_variables["user_data_root_path"] / folder / sub).mkdir(
                exist_ok=True
            )

    logger.debug(
        f"Project structure created at {global_variables["user_data_root_path"].resolve()}"
    )

    # Check if the desktop.ini file exists in the user data root path.
    # If the file exists, the project structure is already set up.
    desktop_ini = global_variables["user_data_root_path"] / "desktop.ini"
    if desktop_ini.exists():
        logger.info(
            "desktop.ini file already exists, project structure is already set up => returning."
        )
        return

    # If the desktop.ini file does not exist, set up the output folder icon.
    logger.debug("desktop.ini file does not exist, setting up output folder icon.")
    # Define and check if icon file exists
    icon_location = (
        global_variables["root_path"] / "resources" / "folder_icon_philanzen.ico"
    )
    if not Path(icon_location).is_file():
        logger.error(
            f"Icon file not found at {icon_location}. Please ensure the icon file exists."
        )
        return

    # Change the icon for the output folder
    # Write desktop.ini
    desktop_ini.write_text(
        f"""[.ShellClassInfo]
IconResource={icon_location},0
IconFile={icon_location}
IconIndex=0
""",
        encoding="utf-8",
    )

    # Hide desktop.ini
    os.system(f'attrib +h "{desktop_ini}"')
    logger.info("Output folder and folder icon set up successfully.")


def toggle_user_data_folder_icon(visible: bool = False) -> None:
    """
    Toggles the visibility of the user data folder icon by modifying its system folder attribute.
    This function uses system commands and Windows API calls to update the folder's attributes
    and notify the system to refresh the icon display in Windows Explorer.
    Args:
        visible (bool): If False, removes the system folder attribute from the user data folder,
                        making it appear as a normal folder. If True, adds the system folder
                        attribute to the user data folder, making it appear as a system folder.
    Returns:
        None
    """
    # NOTE: In order to display the custom folder icon, the folder must be marked as a system folder.
    if visible == False:
        # Force Explorer to reload the folder icon with the system folder attribute removed
        os.system(
            f'attrib -s "{global_variables["user_data_root_path"]}"'
        )  # Removed system folder attribute
        time.sleep(0.1)  # Allow time for the attribute to update
        ctypes.windll.shell32.SHChangeNotify(0x8000000, 0x1000, None, None)
        return
    elif visible == True:
        # Force Explorer to reload the folder icon with the system folder attribute added
        os.system(
            f'attrib +s "{global_variables["user_data_root_path"]}"'
        )  # Added system folder attribute
        time.sleep(0.1)  # Allow time for the attribute to update
        ctypes.windll.shell32.SHChangeNotify(0x8000000, 0x1000, None, None)


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


def update_csv_format_in_global_variables() -> None:
    """
    Updates the global variable `csv_format` with the value specified in the settings.
    This function retrieves the application settings using the `load_settings` function,
    accesses the `csv_format` value from the settings under the "data" section, and updates
    the `global_variables` dictionary with this value.
    Returns:
        None
    """

    settings = load_settings()
    global_variables["csv_format"] = settings["data"]["csv_format"]


def save_dataframe_to_csv(df: DataFrame, filename: str) -> None:
    """
    Save a pandas DataFrame to a CSV file with configurable formatting.
    This function saves a DataFrame to a CSV file in a directory specified by
    the global variable `user_data_root_path`. The CSV formatting (e.g.,
    separator and decimal symbol) is determined by the `csv_format` key in
    the `global_variables` dictionary. If the format is "de", the CSV will
    use a semicolon as the separator and a comma as the decimal symbol. If
    the format is "us", the CSV will use a comma as the separator and a dot
    as the decimal symbol. If no format is specified, default pandas
    settings are used.
    Args:
        df (pd.DataFrame): The DataFrame to save.
        filename (str): The name of the file (without extension) to save the
            DataFrame to.
    Raises:
        Exception: If an error occurs during the saving process, it is
            logged and re-raised.
    """
    try:
        file_path = global_variables["user_data_root_path"] / "data" / f"{filename}.csv"

        if "csv_format" not in global_variables:
            update_csv_format_in_global_variables()

        format = global_variables["csv_format"]
        if format == "de":
            # Set the decimal separator to comma for German format
            df.to_csv(
                file_path,
                index=False,
                sep=";",
                decimal=",",
            )
        elif format == "us":
            # Set the decimal separator to dot for US format
            df.to_csv(
                file_path,
                index=False,
                sep=",",
                decimal=".",
            )
        else:
            # Save in the standard python format if no valid format is given
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


def simple_countdown(seconds: int, animation_type: str = "cycle") -> None:
    """
    Displays a simple countdown timer with an optional animation effect.

    Args:
        seconds (int): The number of seconds for the countdown.
        animation_type (str, optional): The type of animation to display during the countdown.
            Options are:
            - "cycle": Cycles through a predefined list of dot patterns.
            - "blink": Displays a blinking dot pattern.
            - Any other value defaults to a static "..." pattern.

    Returns:
        None
    """

    dot_patterns = ["...  ", ".... ", "....."]
    pattern_number: int = 0

    for remaining in range(seconds, 0, -1):
        if animation_type == "cycle":
            pattern = dot_patterns[pattern_number]
            pattern_number = pattern_number + 1
        elif animation_type == "blink":
            pattern = "..." + ("." if remaining % 2 == 0 else " ")
        else:
            pattern = "..."

        # Resets the pattern number if it exceeds the length of the list
        if pattern_number >= len(dot_patterns):
            pattern_number = 0

        print(f"{pattern}", end="\r")
        time.sleep(1)

    # Clear the line after countdown
    print(" " * 10, end="\r")
