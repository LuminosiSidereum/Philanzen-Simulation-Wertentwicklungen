import logging
import pandas as pd  # type: ignore
from pandas import DataFrame
from simulation import utils
import numpy as np  # type: ignore
import os

logger = logging.getLogger(__name__)


def calculate_inflated_capital(
    inflation_rate: float,
    years: float,
    capital: float,
) -> float:
    """
    Calculate the inflated capital after a given number of years.

    Parameters:
        inflation_rate (float): The yearly inflation rate in percentage.
        years (float): The number of years to simulate.
        capital (float): The initial capital.

    Returns:
        float: The capital value adjusted for inflation after the given years.
    """

    capital_inflated = capital * (1 - (inflation_rate / 100)) ** years
    capital_inflated = round(capital_inflated, 2)
    return capital_inflated


def run_inflation_calculation(
    capital: float,
    bread_price: float,
    inflation_rate: float,
    inflation_period: float,
    currency: str,
    language: str,
) -> list:
    """
    Simulates the effects of inflation on a given capital over a specified period
    and generates a summary of the results.

    Args:
        capital (float): The initial amount of capital.
        bread_price (float): The current price of a single unit of bread.
        inflation_rate (float): The annual inflation rate (as a percentage).
        inflation_period (float): The duration of the inflation period in years.
        currency (str): The currency in which the capital is denominated.
        language (str): The language code for localization of output text.

    Returns:
        list: A list containing the simulation results, including:
            - duration (float): The inflation period in years.
            - inflation_rate (float): The annual inflation rate.
            - capital_amount (float): The initial capital amount.
            - capital_inflated (float): The capital amount after inflation.
            - bread_price (float): The price of bread.
            - bread_current_amount (float): The number of bread units that can be
              purchased with the initial capital.
            - bread_future_amount (float): The number of bread units that can be
              purchased with the inflated capital.
            - currency (str): The currency used in the simulation.

    Raises:
        KeyError: If a required key is missing in the localized output text JSON.

    Notes:
        - The function logs the process of creating the inflation summary.
        - The results are saved to a CSV file using a filename specified in the
          localized output text JSON.
    """

    logger.info(f"Creating an inflation summary for {capital = }")

    capital_inflated = calculate_inflated_capital(
        inflation_rate=inflation_rate, years=inflation_period, capital=capital
    )
    # Calculate the capital lost due to inflation
    breads_current_amount = round((capital / bread_price), 1)
    breads_new_amount = round((capital_inflated / bread_price), 1)

    # Save the simulation results
    plan_keys = [
        "duration",  # 0 (float)
        "inflation_rate",  # 1 (float)
        "capital_amount",  # 2 (float)
        "capital_inflated",  # 3 (float)
        "bread_price",  # 4 (float)
        "bread_current_amount",  # 5 (float)
        "bread_future_amount",  # 6 (float)
        "currency",  # 7 (str)
    ]
    output_text: dict = utils.load_text_json(
        language=language, interface="inflation_model", filename="output_text"
    )
    try:
        col_names: list[str] = [output_text[key] for key in plan_keys]
        logger.debug(f"Resolved column names: {col_names}")
    except KeyError as e:
        msg = f"Missing expected key in JSON: {e}"
        logger.error(msg)
        raise KeyError

    df_inflation_summary = pd.DataFrame(
        data=[
            [
                inflation_period,
                inflation_rate,
                capital,
                capital_inflated,
                bread_price,
                breads_current_amount,
                breads_new_amount,
                currency,
            ]
        ],
        columns=col_names,
    )
    logger.debug(f"DataFrame created:\n{df_inflation_summary.head()}")

    utils.save_dataframe_to_csv(
        df=df_inflation_summary, filename=output_text["file_name_inflation_simulation"]
    )
    return df_inflation_summary.iloc[0].values.tolist()


def execute_simulation(language: str = "de", currency: str = "EUR") -> None:
    """
    Executes the inflation simulation by loading user interface text, gathering user inputs,
    performing calculations, and displaying the results.
    Args:
        language (str): The language code for the user interface text. Defaults to "de".
        currency (str): The currency code for the simulation. Defaults to "EUR".
    Returns:
        None
    Raises:
        KeyError: If required keys are missing in the loaded UI text or settings.
        ValueError: If user inputs are invalid or cannot be converted to float.
    Workflow:
        1. Loads the user interface text for the inflation simulation based on the specified language.
        2. Displays a welcome message and prompts the user for simulation parameters:
           - Initial capital
           - Inflation period
           - Bread price
        3. Retrieves the yearly inflation rate from the settings.
        4. Performs the inflation calculation using the provided inputs.
        5. Displays a summary of the simulation results, including:
           - Adjusted capital
           - Adjusted bread price
           - Other relevant metrics
        6. Clears the screen and waits for user input to return to the homescreen.
    Notes:
        - Logs the execution process and errors using the logger.
        - Ensures the summary is not empty before displaying results.
        - Handles platform-specific screen clearing (Windows or Unix-based systems).
    """

    logger.info("Executing the inflation simulation.")
    # Load the UI text for the inflation simulation
    ui_text: dict = utils.load_text_json(
        language=language, interface="inflation_model", filename="ui_text"
    )

    for dialog in ui_text["welcome_text"].values():
        print(dialog)
    print(f"{currency}")
    # Get the simulation parameters
    inflation_rate = utils.load_settings()["financial"]["yearly_inflation_rate"]
    print(f"{ui_text["inflation_rate"]}{inflation_rate}")
    capital = utils.user_input_float(
        f"{ui_text["capital"]} | {currency}: ", ui_text["invalid_input"]
    )
    inflation_period = utils.user_input_float(
        f"{ui_text["inflation_period"]}", ui_text["invalid_input"]
    )
    bread_price = utils.user_input_float(
        f"{ui_text["bread_price"]} | {currency}: ", ui_text["invalid_input"]
    )
    summary: list = run_inflation_calculation(
        capital=capital,
        bread_price=bread_price,
        inflation_rate=inflation_rate,
        inflation_period=inflation_period,
        currency=currency,
        language=language,
    )

    # Check if the summary is empty before printing
    if not summary:
        logger.error("Summary is empty. No calculation was performed.")
        return

    # Prints the summary of the simulation results before returning to the homescreen
    os.system("cls" if os.name == "nt" else "clear")
    for i, dialog in enumerate(ui_text["summary"].values()):
        if i == 0:
            print(dialog)
            continue
        if i == 3 or i == 4 or i == 5:
            print(f"{dialog} | {currency}: {summary[i-1]}")
            continue
        print(f"{dialog}{summary[i-1]}")

    input(ui_text["return_to_homescreen"])
    logger.info(
        "User returns to the homescreen after successful execution of the simulation."
    )
    return
