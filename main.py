import logging
from simulation import credit_simulation, wealth_projection, utils


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("financial_simulations.log")],
)
logger = logging.getLogger(__name__)


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


def run_simulation_interface():
    ui_text: dict = utils.load_ui_text(language="de", interface="homescreen")  # type: ignore

    print(ui_text["mode_selection_request"])
    for mode_name in ui_text["modes"].values():
        print(mode_name)

    user_choice = select_simulation(ui_text=ui_text)
    if user_choice == 0:
        wealth_projection.execute_simulation()
    elif user_choice == 1:
        credit_simulation.execute_simulation()
    elif user_choice == 2:
        pass
    elif user_choice == 3:
        pass
    else:
        logger.error(
            f"Unhandled and invalid mode selection made by user. Mode selection: {user_choice}"
        )
        quit()


if __name__ == "__main__":
    run_simulation_interface()
