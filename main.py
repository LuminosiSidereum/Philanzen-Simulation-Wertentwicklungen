import logging
import os
from simulation import credit_simulation, wealth_projection, inflation_model, utils
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

valid_user_inputs: dict[str,list] = {
    "modes": [0, 1, 2, 3],
    "settings": [99],
    "quit": ["quit", "q", "exit", "e", "stop", "close"]
}


# MARK: Project Wide Setup Functions
# Configure root logger
def configure_logging():
    Path("log").mkdir(
        parents=True, exist_ok=True
    )  # Create log directory if it doesn't exist

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)  # Set base level for all loggers

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # File handler with rotation
    file_handler = TimedRotatingFileHandler(
        "log/financial_simulations.log",
        when="midnight",
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    # Add handlers (remove existing ones first to avoid duplicates)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    root_logger.addHandler(file_handler)


# Project Structure Setup
def setup_project_structure(base_path: str = ".") -> None:
    """Creates the required folder structure for the project."""
    structure = {
        "data": ["input", "output"],
        "log": [],
        "resources": [],
        "simulation": [],
    }

    for folder, subfolders in structure.items():
        (Path(base_path) / folder).mkdir(parents=True, exist_ok=True)
        for sub in subfolders:
            (Path(base_path) / folder / sub).mkdir(exist_ok=True)

    logging.info(f"Project structure created at {Path(base_path).resolve()}")


# MARK: Functions
def validate_user_selection(*, ui_text: dict) -> int:
    while True:
        try:
            number_input: int = -1
            user_input:str = input(ui_text["input_action_selection"])
            user_input = user_input.strip()

            if user_input.isdigit():
                number_input = int(user_input)
            if number_input in valid_user_inputs["modes"] or user_input in valid_user_inputs["settings"]:
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
    if user_choice == 0:
        raise NotImplementedError(
            f"Simulation is not implemented yet. {user_choice = }"
        )
    elif user_choice == 1:
        credit_simulation.execute_simulation(settings["ui"]["language"], settings["financial"]["currency"])
    elif user_choice == 2:
        inflation_model.execute_simulation(settings["ui"]["language"], settings["financial"]["currency"]) 
    elif user_choice == 3:
        raise NotImplementedError(
            f"Simulation is not implemented yet. {user_choice = }"
        )
    elif user_choice == 99:
        raise NotImplementedError(
            f"Change the Settings is not implemented yet. {user_choice = }"
        )
    else:
        logger.error(
            f"Unhandled and invalid mode selection made by user. {user_choice = }"
        )


def run_simulation_interface():
    settings: dict = utils.load_settings()  # type: ignore
    ui_text: dict = utils.load_text_json(language=settings["ui"]["language"], interface="homescreen", filename="ui_text")  # type: ignore
    logger.debug(f"Loaded settings and UI text.")

    logger.info("Starting financial simulations.")
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
    except NotImplementedError as e:
        logger.error(f"Not implemented: {e}")


if __name__ == "__main__":
    print("...")
    configure_logging()
    logger = logging.getLogger(__name__)
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        run_simulation_interface()
