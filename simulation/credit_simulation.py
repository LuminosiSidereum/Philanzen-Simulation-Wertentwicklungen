import pandas as pd  # type: ignore
from pandas import DataFrame  # type: ignore
import logging
import numpy as np
from simulation import utils

logger = logging.getLogger(__name__)


def _input_downpayment_monthly(
    credit: float, interest: float, ui_text: dict, currency: str = "EUR"
) -> float:
    # Claculates the interest amount for the first month
    interest_amount: float = credit * (interest / 100 / 12)
    print(f"{ui_text["credit_interest_monthly"]}: {interest_amount:.2f}")
    # Asks the user for the monthly repayment amount and checks if it is smaller than the interest amount
    # If it is, it asks for the amount again and prints the interest amount as wekk as the repayment amount
    while True:
        repayment: float = utils.user_input_float(
            ui_text["credit_downpayment_monthly"], ui_text["invalid_input"]
        )
        if repayment < interest_amount:
            for dialog in ui_text["input_downpayment_monthly"].values():
                print(dialog)
            print(
                f"{ui_text["credit_interest_monthly"]}: {interest_amount:.2f} {currency}"
            )
            print(
                f"{ui_text["credit_downpayment_monthly"]}: {repayment:.2f} {currency}"
            )
        else:
            return repayment


def _credit_calculation_downpayment_monthly_values(
    df_credit: DataFrame, col_names: list, interest: float, repayment: float
) -> DataFrame:
    current_credit_balance: float = df_credit.iloc[-1][col_names[1]]
    # Calculates the interest amount
    interest_amount: float = current_credit_balance * (interest / 100 / 12)
    # Calculates the remaining credit balance
    # The remaining credit balance is the current credit balance plus the interest amount minus the repayment amount
    remaining_credit_balance: float = np.subtract(
        np.add(current_credit_balance, interest_amount), repayment
    )
    # Creates a new DataFrame with the new values
    df_new_values = pd.DataFrame(
        data=[
            [
                df_credit.iloc[-1][col_names[0]] + 1,
                remaining_credit_balance,
                interest_amount,
                repayment,
            ]
        ],
        columns=col_names,
    )
    # Concatenates the new DataFrame with the old one
    pd.concat([df_credit, df_new_values], ignore_index=True, inplace=True)
    return df_credit


def _credit_calculation_downpayment_final_payment(
    df_credit: DataFrame, col_names: list, interest: float
) -> DataFrame:
    current_credit_balance: float = df_credit.iloc[-1][col_names[1]]
    # Calculates the interest amount
    interest_amount: float = current_credit_balance * (interest / 100 / 12)
    # Calculates the final payment amount
    final_payment: float = np.add(current_credit_balance, interest_amount)
    # Creates a new DataFrame with the new values
    df_new_values = pd.DataFrame(
        data=[
            [
                df_credit.iloc[-1][col_names[0]] + 1,
                0,
                interest_amount,
                final_payment,
            ]
        ],
        columns=col_names,
    )
    # Concatenates the new DataFrame with the old one
    pd.concat([df_credit, df_new_values], ignore_index=True, inplace=True)
    return df_credit


def _calculation_selection(ui_text: dict) -> int:
    while True:
        try:
            user_input = int(input(ui_text["user_input_calculation_selection"]))
            if user_input in [0, 1]:
                return user_input
            else:
                print(ui_text["invalid_input"])
        except ValueError:
            print(ui_text["invalid_input"])


def _execute_calculation_downpayment(
    credit: float, interest: float, repayment: float, currency: str = "EUR"
) -> None:
    # Load your text configuration
    output_columns = utils.load_text_json(
        language="de", interface="credit_simulation", filename="output_text"
    )

    # Validate and extract colum names
    plan_keys = [
        "duration",
        "remaining_credit",
        "interest_payment",
        "monthly_downpayment",
    ]
    try:
        col_names: list[str] = [
            output_columns["downpayment_plan"][key] for key in plan_keys
        ]
        logger.debug(f"Resolved column names: {col_names}")
    except KeyError as e:
        msg = f"Missing expected key in JSON: {e}"
        logger.error(msg)
        raise ValueError(msg)

    # Create DataFrame
    logger.info(f"Creating calculation_downpayment DataFrame ({credit = })")
    df_credit_monthly = pd.DataFrame(data=[[0, credit, 0, 0]], columns=col_names)

    logger.debug(f"DataFrame created:\n{df_credit_monthly.head()}")

    while df_credit_monthly.iloc[-1][col_names[1]] > repayment:
        df_credit_monthly = _credit_calculation_downpayment_monthly_values(
            df_credit=df_credit_monthly,
            col_names=col_names,
            interest=interest,
            repayment=repayment,
        )
        logger.debug(f"Updated DataFrame:\n{df_credit_monthly.tail()}")
    df_credit_monthly = _credit_calculation_downpayment_final_payment(
        df_credit=df_credit_monthly,
        col_names=col_names,
        interest=interest,
    )
    logger.debug(f"Final DataFrame:\n{df_credit_monthly.tail()}")
    
    # Summary of the credit details
    # Validate and extract colum names for the summary
    plan_keys = [
        "credit_amount",
        "duration",
        "monthly_downpayment",
        "total_interest",
        "total_cost"
        "currency"
    ]
    try:
        col_names_summary: list[str] = [
            output_columns["downpayment_plan"][key] for key in plan_keys
        ]
        logger.debug(f"Resolved column names: {col_names}")
    except KeyError as e:
        msg = f"Missing expected key in JSON: {e}"
        logger.error(msg)
        raise ValueError(msg)
    # Create a new DataFrame that summarizes the credit details
    df_credit_summary = pd.DataFrame(
        data=[
            [
                credit,
                df_credit_monthly.iloc[-1][col_names[0]],
                repayment,
                df_credit_monthly[col_names[2]].sum(),
                df_credit_monthly[col_names[2]].sum()+credit,
                currency
            ]
        ],
        columns=col_names,
    )
    
def execute_simulation(language: str = "de", currency: str = "EUR") -> None:
    """
    Execute the credit simulation.
    """
    ui_text: dict = utils.load_text_json(
        language=language, interface="credit_simulation", filename="ui_text"
    )
    for dialog in ui_text["welcome_text"].values():
        print(dialog)
    print(f"{currency}")
    calculation_selection: int = _calculation_selection(ui_text)

    credit_amout: float = utils.user_input_float(
        ui_text["credit_amount"], ui_text["invalid_input"]
    )
    interest_rate: float = utils.user_input_float(
        ui_text["credit_interest_rate"], ui_text["invalid_input"]
    )

    if calculation_selection == 0:
        downpayment: float = _input_downpayment_monthly(
            credit=credit_amout,
            interest=interest_rate,
            ui_text=ui_text,
            currency=currency,
        )
        _execute_calculation_downpayment(
            credit_amout, interest_rate, downpayment, currency
        )

    elif calculation_selection == 1:
        duration: int = utils.user_input_int(
            ui_text["credit_duration"], ui_text["invalid_input"]
        )
