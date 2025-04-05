import logging
import os
from simulation import credit_simulation, wealth_projection, utils
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


# Configure root logger
def configure_logging():
    Path("log").mkdir(parents=True, exist_ok=True)  # Create log directory if it doesn't exist
    
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)  # Set base level for all loggers

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # File handler with rotation
    file_handler = TimedRotatingFileHandler(
        "log/financial_simulations.log", when="midnight", backupCount=7, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # Add handlers (remove existing ones first to avoid duplicates)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    root_logger.addHandler(file_handler)


# MARK: Functions
def select_simulation(*, ui_text: dict) -> int:
    while True:
        try:
            user_input = int(input(ui_text["mode_selection_input"]))
            if user_input in range(len(ui_text["modes"])):
                return user_input
            else:
                print(ui_text["invalid_mode_selection"])
        except ValueError:
            print(ui_text["invalid_input"])

def execute_selected_simulation(user_choice: int):
    if user_choice == 0:
        raise NotImplementedError(f"Simulation is not implemented yet. {user_choice = }")
    elif user_choice == 1:
        credit_simulation.execute_simulation() #Language and Currency selection needs to be implemented; currently using standard values
    elif user_choice == 2:
        raise NotImplementedError(f"Simulation is not implemented yet. {user_choice = }")
    elif user_choice == 3:
        raise NotImplementedError(f"Simulation is not implemented yet. {user_choice = }")
    else:
        logger.error(
            f"Unhandled and invalid mode selection made by user. Mode selection: {user_choice}"
        )


def run_simulation_interface():
    settings: dict = utils.load_settings()  # type: ignore
    ui_text: dict = utils.load_text_json(language=settings["ui"]["language"], interface="homescreen", filename="ui_text")  # type: ignore
    logger.debug(f"Loaded settings and UI text.")

    logger.info("Starting financial simulations.")
    print(ui_text["mode_selection_request"])
    for mode_name in ui_text["modes"].values():
        print(mode_name)

    user_choice = select_simulation(ui_text=ui_text)
    os.system("cls" if os.name == "nt" else "clear")
    for dialogue in ui_text["general_input_information"].values():
        print(dialogue)
    input(ui_text["user_confirmation"])
    os.system("cls" if os.name == "nt" else "clear")
    try:
        execute_selected_simulation(user_choice)
    except NotImplementedError as e:
        logger.error(f"Not implemented: {e}")


if __name__ == "__main__":
    print("...")
    configure_logging()
    logger = logging.getLogger(__name__)
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        run_simulation_interface()
