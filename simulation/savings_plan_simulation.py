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


def _calculate_monthly_values(
    df_savings: DataFrame, col_names: list[str], interest_rate: float, monthly_payment: float, savings_amount: float 
) -> DataFrame:
    interest_amount: float = df_savings.iloc[-1][col_names[1]] * (interest_rate / 100 / 12)
    
    # Checks if a full monthly payment is needed or if a smaller payment is needed to reach the savings goal
    if df_savings.iloc[-1][col_names[1]] + interest_amount + monthly_payment >= savings_amount:
       monthly_payment = savings_amount - df_savings.iloc[-1][col_names[1]] - interest_amount
    
    # Create a new DataFrame with the updated values 
    df_new_values: DataFrame = pd.DataFrame(
        data=[
            [

            df_savings.iloc[-1][col_names[0]] + 1,
            df_savings.iloc[-1][col_names[1]] + monthly_payment + interest_amount,
            interest_amount,
            monthly_payment
            ]],
        columns=col_names
    )
    # Concatenates the new DataFrame with the old one
    df_savings = pd.concat([df_savings, df_new_values], ignore_index=True)
    return df_savings
    
    
    

def run_savings_plan_calculation(
    savings_amount: float,
    interest_rate: float,
    savings_rate: float,
    currency: str,
    language: str,
) -> list:

    logger.info(f"Creating savings plan for ({savings_amount = })")

    # Load your text configuration
    output_text: dict = utils.load_text_json(
        language=language, interface="savings_plan", filename="output_text"
    )

    # Validate and extract colum names
    plan_keys: list = [
        "duration",
        "savings_amount",
        "interest_amount",
        "monthly_payment",
    ]
    try:
        col_names_simulation: list[str] = [output_text[key] for key in plan_keys]
        logger.debug(f"Resolved column names: {col_names_simulation}")
    except KeyError as e:
        msg = f"Missing expected key in JSON: {e}"
        logger.error(msg)
        raise ValueError

    # Create DataFrame
    df_savings_plan = pd.DataFrame(
        data=[[0, savings_rate, 0, savings_rate]], columns=col_names_simulation
    )
    logger.debug(f"DataFrame created:\n{df_savings_plan.head()}")

    # Calculate the monthly downpayment values until the remaining credit balance is less than the repayment amount
    # The last row of the DataFrame is used to check if the remaining credit balance is greater than the repayment amount
    print("...")
    while df_savings_plan.iloc[-1][col_names_simulation[1]] < savings_amount:
        df_savings_plan = _calculate_monthly_values(
            df_savings=df_savings_plan,
            col_names=col_names_simulation,
            interest_rate=interest_rate,
            monthly_payment=savings_rate,
            savings_amount=savings_amount
        )
        logger.debug(f"Updated DataFrame:\n{df_savings_plan.tail()}")

    # Summary of the credit details
    # Validate and extract colum names for the summary
    plan_keys = [
        "savings_amount",  # 0 (float)
        "interest_rate",  # 1 (float)
        "duration",  # 2 (int)
        "monthly_payment",  # 3 (float)
        "total_interest",  # 4 (float)
        "total_saved",  # 5 (float)
        "currency",  # 6 (str)
    ]
    try:
        col_names_summary: list[str] = [output_text[key] for key in plan_keys]
        logger.debug(f"Resolved column names: {col_names_summary}")
    except KeyError as e:
        msg = f"Missing expected key in JSON: {e}"
        logger.error(msg)
        raise ValueError

    # Create a new DataFrame that summarizes the credit details
    df_savings_summary = pd.DataFrame(
        data=[
            [
                savings_amount,
                interest_rate,
                df_savings_plan.iloc[-1][col_names_simulation[0]],
                savings_rate,
                df_savings_plan[col_names_simulation[2]].sum().round(2),
                df_savings_plan[col_names_simulation[3]].sum().round(2),
                currency,
            ]
        ],
        columns=col_names_summary,
    )
    df_savings_summary = df_savings_summary.astype({col_names_summary[2]: int})

    # Save the DataFrames to CSV files
    utils.save_dataframe_to_csv(df=df_savings_plan, filename=output_text["file_name_savings_simulation"])
    utils.save_dataframe_to_csv(
        df=df_savings_summary, filename=output_text["file_name_savings_summary"]
    )

    return df_savings_summary.iloc[0].values.tolist()


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
        ui_text_input_request=f"{ui_text["savings_amount"]} | {currency}: ",
        ui_text_invalid_input=ui_text["invalid_input"],
    )
    interest_rate: float = utils.user_input_float(
        ui_text["interest_rate"], ui_text["invalid_input"]
    )

    summary: list = []
    savings_rate: float

    # Sets the savings rate based on the user selection
    if calculation_selection == 0:
        savings_rate = utils.user_input_float(
            ui_text_input_request=f"{ui_text["savings_rate"]} | {currency}: ",
            ui_text_invalid_input=ui_text["invalid_input"],
        )
    elif calculation_selection == 1:
        savings_period: int = utils.user_input_int(
            ui_text["savings_period"], ui_text["invalid_input"]
        )
        savings_rate = utils.calculate_monthly_payment_from_duration(
            target_amount=savings_amount,
            annual_interest_rate=interest_rate,
            duration_months=savings_period,
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
        if i == 2 or i == 3:
            print(f"{dialog}{summary[i-1]}")
            continue
        print(f"{dialog} | {currency}: {summary[i-1]}")

    input(ui_text["return_to_homescreen"])
    logger.info("User returns to the homescreen after successfull execution of the simulation.")
    return
