import logging
import os
from simulation import (
    credit_simulation,
    wealth_projection,
    inflation_model,
    utils,
    savings_plan_simulation,
)
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

valid_user_inputs: dict[str, list] = {
    "modes": [0, 1, 2, 3],
    "settings": [99],
    "quit": ["quit", "q", "exit", "e", "stop", "close"],
}


# MARK: Project Wide Setup Functions
# Configure root logger
def configure_logging() -> Path:
    """
    Configures the logging system for the application.
    This function sets up a logging system that writes log messages to a file
    with daily rotation and retains logs for up to 7 days. It ensures that the
    log directory exists, removes any existing handlers from the root logger
    to prevent duplicates, and applies a consistent log message format.

    Log Details:
    - Log directory: "log/"
    - Log file: "financial_simulations.log"
    - Rotation: Daily at midnight
    - Backup count: 7 days
    - Encoding: UTF-8
    - Format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    Raises:
        OSError: If the log directory cannot be created.

    Returns:
        Path: The path to the log file.
    """

    Path("log").mkdir(
        parents=True, exist_ok=True
    )  # Create log directory if it doesn't exist

    log_Path = Path("log/financial_simulations.log")

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)  # Set base level for all loggers

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # File handler with rotation
    file_handler = TimedRotatingFileHandler(
        filename=log_Path,
        when="midnight",
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    # Add handlers (remove existing ones first to avoid duplicates)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    root_logger.addHandler(file_handler)

    return log_Path


# Project Structure Setup
def setup_project_structure(base_path: str = ".") -> None:
    """
    Creates the required folder structure for the project.

    Args:
        base_path (str): The base directory where the project structure will be created.
                         Defaults to the current directory (".").

    Notes:
        - The function ensures that the necessary directories for the project are created.
        - If the directories already exist, they will not be recreated.
        - Logs the location of the created project structure.
    """
    structure = {
        "data": ["input", "output"],
        "docs": [],
        "log": [],
        "resources": [],
        "simulation": [],
    }

    for folder, subfolders in structure.items():
        (Path(base_path) / folder).mkdir(parents=True, exist_ok=True)
        for sub in subfolders:
            (Path(base_path) / folder / sub).mkdir(exist_ok=True)

    logger.debug(f"Project structure created at {Path(base_path).resolve()}")


# MARK: Functions
def validate_user_selection(*, ui_text: dict) -> int:
    """
    Validates the user's selection from the input and returns the corresponding integer value.
    This function continuously prompts the user for input until a valid selection is made. It checks
    if the input is a valid mode, setting, or quit command. If the input is valid, it returns the
    corresponding integer value. If the user requests to quit, the program exits gracefully.
    Args:
        ui_text (dict): A dictionary containing user interface text, including prompts and error messages.
            Expected keys:
                - "input_action_selection": Prompt text for user input.
                - "invalid_action_selection": Error message for invalid input.
    Returns:
        int: The validated integer corresponding to the user's selection.
    Raises:
        Exception: Logs and exits the program if an unexpected error occurs during input validation.
    Notes:
        - The function relies on external variables `valid_user_inputs` and `logger` for validation
          and logging, respectively.
        - The `valid_user_inputs` dictionary is expected to have the following keys:
            - "modes": A list of valid integer inputs for modes.
            - "settings": A list of valid string inputs for settings.
            - "quit": A list of valid string inputs to quit the program.
    """

    while True:
        try:
            number_input: int = -1
            user_input: str = input(ui_text["input_action_selection"])
            user_input = user_input.strip()

            if user_input.isdigit():
                number_input = int(user_input)
            if (
                number_input in valid_user_inputs["modes"]
                or user_input in valid_user_inputs["settings"]
            ):
                return number_input

            user_input = user_input.lower()
            if user_input in valid_user_inputs["quit"]:
                logger.info("User requested to quit the program.")
                quit()

            print(ui_text["invalid_action_selection"])
        except Exception as e:
            logger.error(f"{user_input = } triggered an error: {e}")
            quit()


def execute_selected_simulation(user_choice: int, settings: dict) -> None:
    """
    Executes a specific simulation based on the user's choice and provided settings.
    Args:
        user_choice (int): The user's selection indicating which simulation to execute.
            - 0: Not implemented.
            - 1: Executes the credit simulation.
            - 2: Executes the inflation model simulation.
            - 3: Not implemented.
            - 99: Not implemented (Change the Settings).
        settings (dict): A dictionary containing configuration settings. Expected keys:
            - "ui": A dictionary with a "language" key specifying the language setting.
            - "financial": A dictionary with a "currency" key specifying the currency setting.
    Raises:
        NotImplementedError: If the selected simulation (user_choice) is not implemented.
        KeyError: If required keys are missing in the settings dictionary.
        ValueError: If an invalid user_choice is provided.
    Logs:
        Logs an error message if an invalid user_choice is made.
    """

    if user_choice == 0:
        logging.critical(f"{user_choice = } is not implemented yet.")
        raise NotImplementedError

    elif user_choice == 1:
        credit_simulation.execute_simulation(
            settings["ui"]["language"], settings["financial"]["currency"]
        )
    elif user_choice == 2:
        inflation_model.execute_simulation(
            settings["ui"]["language"], settings["financial"]["currency"]
        )
    elif user_choice == 3:
        savings_plan_simulation.execute_simulation(
            settings["ui"]["language"], settings["financial"]["currency"]
        )
    elif user_choice == 99:
        logging.critical(f"{user_choice = } is not implemented yet.")
        raise NotImplementedError
    else:
        logger.error(
            f"Unhandled and invalid mode selection made by user. {user_choice = }"
        )


def run_simulation_interface():
    """
    Executes the main interface for running financial simulations.
    This function loads the necessary settings and UI text, displays a menu
    for the user to select an action, and processes the user's choice. It
    clears the console at appropriate points, provides general input
    information, and executes the selected simulation. If the selected
    simulation is not implemented, an error is logged.
    Steps:
    1. Load settings and UI text.
    2. Display action selection menu to the user.
    3. Validate the user's selection.
    4. Display general input information and wait for user confirmation.
    5. Execute the selected simulation.
    Raises:
        NotImplementedError: If the selected simulation is not implemented.
    Note:
        - The function uses external utility functions `load_settings` and
          `load_text_json` to load configuration and UI text.
        - The function clears the console using `os.system` for better user
          experience.
    """
    logger.info(f"Run the homescreen interface")

    settings: dict = utils.load_settings()  # type: ignore
    ui_text: dict = utils.load_text_json(language=settings["ui"]["language"], interface="homescreen", filename="ui_text")  # type: ignore
    logger.debug(f"Loaded settings and UI text.")

    print(ui_text["request_action_selection"])
    for action_name in ui_text["action"].values():
        print(action_name)

    user_choice = validate_user_selection(ui_text=ui_text)
    os.system("cls" if os.name == "nt" else "clear")
    for dialogue in ui_text["general_input_information"].values():
        print(dialogue)
    input(ui_text["user_confirmation"])
    os.system("cls" if os.name == "nt" else "clear")
    try:
        execute_selected_simulation(user_choice, settings)
    except NotImplementedError:
        print(ui_text["error"]["NotImplemented"])
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")
        for dialogue in ui_text["error"]["UnhandledException"].values():
            print(dialogue)
        print(f"{log_Path}")
        utils.simple_countdown(6)


if __name__ == "__main__":
    print("...")
    log_Path = configure_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting the financial simulation program.")
    setup_project_structure()
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        run_simulation_interface()