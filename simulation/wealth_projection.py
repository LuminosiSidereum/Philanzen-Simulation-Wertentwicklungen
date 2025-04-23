import pandas as pd  # type: ignore
from pandas import DataFrame  # type: ignore
import logging
import os
from simulation import utils
from simulation.inflation_model import calculate_inflated_capital

logger = logging.getLogger(__name__)


def _selection_automatic_adjustement(ui_text: dict) -> int:
    while True:
        try:
            user_input = int(
                input(ui_text["user_input_selection_automatic_adjustement"])
            )
            if user_input in [0, 1]:
                return user_input
            else:
                print(ui_text["invalid_input"])
        except ValueError:
            print(ui_text["invalid_input"])


def _calculate_monthly_values(
    df_wealth: DataFrame, col_names: list, interest_rate: float, monthly_savings: float
) -> DataFrame:
    current_balance: float = df_wealth.iloc[-1][col_names[1]]
    # Calculates the interest amount
    interest_amount: float = current_balance * (interest_rate / 100 / 12)
    # Calculates the remaining credit balance
    # The remaining credit balance is the current credit balance plus the interest amount minus the repayment amount
    new_balance: float = current_balance + interest_amount + monthly_savings
    # Creates a new DataFrame with the new values
    df_new_values = pd.DataFrame(
        data=[
            [
                df_wealth.iloc[-1][col_names[0]] + 1,
                new_balance,
                interest_amount,
                monthly_savings,
            ]
        ],
        columns=col_names,
    )
    # Concatenates the new DataFrame with the old one
    df_wealth = pd.concat([df_wealth, df_new_values], ignore_index=True)
    return df_wealth


def run_wealth_projection_calculation(
    inital_balance: float,
    interest_rate: float,
    savings_rate: float,
    period_years: int,
    automatic_adjustement: int,
    currency: str,
    language: str,
) -> list:

    logger.info(
        "Starting the wealth projection calculation with the following parameters: "
        f"Initial balance: {inital_balance}, Interest rate: {interest_rate}, "
        f"Savings rate: {savings_rate}, Period years: {period_years}, "
        f"Automatic adjustment: {automatic_adjustement}"
    )

    # Load your text configuration
    output_text: dict = utils.load_text_json(
        language=language, interface="wealth_projection", filename="output_text"
    )

    # Validate and extract colum names
    plan_keys: list = [
        "duration",  # 0 (float)
        "balance",  # 1 (float)
        "interest_amount",  # 2 (float)
        "monthly_savings",  # 3 (float)
    ]
    try:
        col_names_simulation: list[str] = [output_text[key] for key in plan_keys]
        logger.debug(f"Resolved column names: {col_names_simulation}")
    except KeyError as e:
        msg = f"Missing expected key in JSON: {e}"
        logger.error(msg)
        raise ValueError

    # Create DataFrame
    df_wealth_projection = pd.DataFrame(
        data=[[0, inital_balance + savings_rate, 0, savings_rate]],
        columns=col_names_simulation,
    )
    logger.debug(f"DataFrame created:\n{df_wealth_projection.head()}")

    for i in range(period_years * 12):
        if automatic_adjustement == 1 and i % 36 == 0 and i != 0:
            savings_rate = round(savings_rate * 1.05, 2)
            logger.debug(f"Automatic adjustment applied: {savings_rate = }")
        # Calculate monthly values
        df_wealth_projection = _calculate_monthly_values(
            df_wealth_projection,
            col_names_simulation,
            interest_rate,
            savings_rate,
        )
    # Summary of the wealth plan
    # Validate and extract colum names for the summary
    plan_keys = [
        "balance",  # 0 (float)
        "inflated_balance",  # 1 (float)
        "duration",  # 2 (int)
        "interest_rate",  # 3 (float)
        "inflation_rate",  # 4 (float)
        "monthly_savings",  # 5 (float)
        "automatic_adjustement",  # 6 (int)
        "total_interest",  # 7 (float)
        "total_saved",  # 8 (float)
        "currency",  # 9 (str)
    ]
    try:
        col_names_summary: list[str] = [output_text[key] for key in plan_keys]
        logger.debug(f"Resolved column names: {col_names_summary}")
    except KeyError as e:
        msg = f"Missing expected key in JSON: {e}"
        logger.error(msg)
        raise ValueError

    final_balance: float = df_wealth_projection.iloc[-1][col_names_simulation[1]].round(
        2
    )
    inflation_rate = utils.load_settings()["financial"]["yearly_inflation_rate"]
    inflation_adjusted_final_balance: float = calculate_inflated_capital(
        inflation_rate, period_years, final_balance
    )
    # Create a new DataFrame with the summary
    df_wealth_projection_summary = pd.DataFrame(
        data=[
            [
                final_balance,
                inflation_adjusted_final_balance,
                period_years,
                interest_rate,
                inflation_rate,
                savings_rate,
                automatic_adjustement,
                df_wealth_projection[col_names_simulation[2]].sum().round(2),
                df_wealth_projection[col_names_simulation[3]].sum().round(2)
                + inital_balance,
                currency,
            ]
        ],
        columns=col_names_summary,
    )

    # df_wealth_projection_summary = df_wealth_projection_summary.astype({col_names_summary[2]: int})

    # Save the DataFrames to a CSV file
    utils.save_dataframe_to_csv(
        df_wealth_projection, output_text["file_name_wealth_projection"]
    )
    utils.save_dataframe_to_csv(
        df_wealth_projection_summary, output_text["file_name_wealth_projection_summary"]
    )

    return df_wealth_projection_summary.iloc[0].values.tolist()


def execute_simulation(language: str = "de", currency: str = "EUR") -> None:
    logger.info("Exectuting the wealth projection simulation")

    ui_text: dict = utils.load_text_json(
        language=language, interface="wealth_projection", filename="ui_text"
    )
    for dialog in ui_text["welcome_text"].values():
        print(dialog)
    print(f"{currency}")

    inital_balance: float = utils.user_input_float(
        ui_text_input_request=f"{ui_text["inital_balance"]} | {currency}: ",
        ui_text_invalid_input=ui_text["invalid_input"],
    )
    interest_rate: float = utils.user_input_float(
        ui_text["interest_rate"], ui_text["invalid_input"]
    )
    savings_rate: float = utils.user_input_float(
        ui_text_input_request=f"{ui_text["savings_rate"]} | {currency}: ",
        ui_text_invalid_input=ui_text["invalid_input"],
    )
    # The user selects if the savings rate should be adjusted automatically, if a savings rate is set
    automatic_adjustement: int = 0
    if savings_rate > 0:
        automatic_adjustement = _selection_automatic_adjustement(ui_text)

    # The user inserts the savings period in years
    period_years: int = utils.user_input_int(
        ui_text["savings_period"], ui_text["invalid_input"]
    )

    summary: list = []

    # Execute the wealth projection calculation
    summary = run_wealth_projection_calculation(
        inital_balance,
        interest_rate,
        savings_rate,
        period_years,
        automatic_adjustement,
        currency,
        language,
    )

    if not summary:
        logger.error("Summary is empty. No calculation was performed.")
        return

    # Prints the summary of the credit details before returning to the homescreen
    os.system("cls" if os.name == "nt" else "clear")

    # TODO: Adjust the dialog texts to the new summary
    for i, dialog in enumerate(ui_text["summary"].values()):
        if i == 0:
            print(dialog)
            continue
        if i == 3 or i == 4 or i == 5 or i == 7:
            print(f"{dialog}{summary[i-1]}")
            continue
        print(f"{dialog} | {currency}: {summary[i-1]}")

    input(ui_text["return_to_homescreen"])
    logger.info(
        "User returns to the homescreen after successfull execution of the simulation."
    )
    return
