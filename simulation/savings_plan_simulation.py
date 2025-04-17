import pandas as pd  # type: ignore
from pandas import DataFrame  # type: ignore
import logging
import numpy as np
import os
from simulation import utils

logger = logging.getLogger(__name__)

def _calculation_selection(ui_text: dict) -> int:
    """
    Prompts the user to select a calculation option and validates the input.
    Args:
        ui_text (dict): A dictionary containing text messages for user interaction.
            Expected keys:
                - "user_input_calculation_selection": Prompt message for user input.
                - "invalid_input": Message displayed when the input is invalid.
    Returns:
        int: The user's selection, either 0 or 1.
    Raises:
        ValueError: If the input cannot be converted to an integer (handled internally).
    """

    while True:
        try:
            user_input = int(input(ui_text["user_input_calculation_selection"]))
            if user_input in [0, 1]:
                return user_input
            else:
                print(ui_text["invalid_input"])
        except ValueError:
            print(ui_text["invalid_input"])

def run_savings_plan_calculation(savings_amount: float, interest_rate: float, savings_rate: float, currency: str, language: str) -> list:
    raise NotImplementedError("This function is not implemented yet.")


def execute_simulation(language: str = "de", currency: str = "EUR") -> None:
    """Execute the savings plan simulation.

    Args:
        language (str, optional): Language for the simulation. Defaults to "de".
        currency (str, optional): Currency for the simulation. Defaults to "EUR".

    Returns:
        None
    """
    logger.info("Exectuting the savings plan simulation")
    
    ui_text: dict = utils.load_text_json(
        language=language, interface="savings_plan", filename="ui_text"
    )
    for dialog in ui_text["welcome_text"].values():
        print(dialog)
    print(f"{currency}")
    
    calculation_selection: int = _calculation_selection(ui_text)
    
    savings_amount: float = utils.user_input_float(
        ui_text_input_request = f"{ui_text["savings_amount"]} | {currency}: ", ui_text_invalid_input = ui_text["invalid_input"]
    )
    interest_rate: float = utils.user_input_float(
        ui_text["interest_rate"], ui_text["invalid_input"]
    )
    
    summary: list = []
    savings_rate: float
    
    # Sets the savings rate based on the user selection
    if calculation_selection == 0:
        savings_rate = utils.user_input_float(
            ui_text_input_request= f"{ui_text["savings_rate"]} | {currency}: ",ui_text_invalid_input= ui_text["invalid_input"]
        )
    elif calculation_selection == 1:
        savings_period: int = utils.user_input_int(
            ui_text["savings_period"], ui_text["invalid_input"]
        )
        savings_rate = utils.calculate_monthly_payment_from_duration(
            target_amount=savings_amount,
            annual_interest_rate=interest_rate,
            duration_months=savings_period
        )


    # Execute the savings plan calculation
    summary = run_savings_plan_calculation(
        savings_amount, interest_rate, savings_rate, currency, language
    )

    if not summary:
        logger.error("Summary is empty. No calculation was performed.")
        return

    # Prints the summary of the credit details before returning to the homescreen
    os.system("cls" if os.name == "nt" else "clear")
    for i, dialog in enumerate(ui_text["summary"].values()):
        if i == 0:
            print(dialog)
            continue
        if i == 2 or i == 4:
            print(f"{dialog}{summary[i-1]}")
            continue
        print(f"{dialog} | {currency}: {summary[i-1]}")

    input(ui_text["return_to_homescreen"])
    logging.info("User returned to the homescreen after successfull credit simulation.")
    return

    