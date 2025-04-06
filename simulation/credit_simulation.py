import pandas as pd  # type: ignore
from pandas import DataFrame  # type: ignore
import logging
import numpy as np
import os
from simulation import utils

logger = logging.getLogger(__name__)


def _input_downpayment_monthly(
    credit: float, interest: float, ui_text: dict, currency: str = "EUR"
) -> float:
    """
    Prompts the user to input a valid monthly repayment amount for a credit.
    This function calculates the monthly interest amount based on the provided credit and interest rate.
    It then repeatedly asks the user for a repayment amount until the input is greater than or equal to
    the calculated interest amount. If the repayment amount is insufficient, it displays relevant messages
    and prompts the user again.
    Args:
        credit (float): The total credit amount.
        interest (float): The annual interest rate (in percentage).
        ui_text (dict): A dictionary containing user interface text for prompts and messages.
        currency (str, optional): The currency symbol to display. Defaults to "EUR".
    Returns:
        float: The valid monthly repayment amount entered by the user.
    """

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
        else:
            return repayment


def _calculate_monthly_downpayment(
    df_credit: DataFrame, col_names: list, interest: float, repayment: float
) -> DataFrame:
    """
    Calculates the monthly values for a credit downpayment simulation and appends the results to the given DataFrame.
    Args:
        df_credit (DataFrame): A DataFrame containing the credit simulation data.
            The last row represents the current state of the credit.
        col_names (list): A list of column names for the DataFrame.
            Expected order: [month, credit_balance, interest_amount, repayment].
        interest (float): The annual interest rate (in percentage) applied to the credit balance.
        repayment (float): The fixed monthly repayment amount.
    Returns:
        DataFrame: The updated DataFrame with an additional row containing the calculated values
        for the next month:
            - Incremented month number.
            - Updated remaining credit balance.
            - Calculated interest amount for the current month.
            - Fixed repayment amount.
    """

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
    df_credit = pd.concat([df_credit, df_new_values], ignore_index=True)
    return df_credit


def _calculate_final_downpayment(
    df_credit: DataFrame, col_names: list, interest: float
) -> DataFrame:
    """
    Calculates the final payment and updates the credit DataFrame with the new values.
    This function computes the interest amount and final payment for a credit balance,
    appends the calculated values as a new row to the provided DataFrame, and returns
    the updated DataFrame.
    Args:
        df_credit (DataFrame): The input DataFrame containing credit information.
            It is expected to have at least two columns:
            - col_names[0]: A column representing the current period or step.
            - col_names[1]: A column representing the current credit balance.
        col_names (list): A list of column names in the DataFrame. The list should
            contain at least two elements:
            - col_names[0]: The name of the column for the period or step.
            - col_names[1]: The name of the column for the credit balance.
        interest (float): The annual interest rate (in percentage) used to calculate
            the interest amount.
    Returns:
        DataFrame: The updated DataFrame with an additional row containing:
            - The next period or step.
            - A zero value for the downpayment.
            - The calculated interest amount.
            - The calculated final payment.
    """

    current_credit_balance: float = df_credit.iloc[-1][col_names[1]]
    # Calculates the interest amount
    interest_amount: float = round(current_credit_balance * (interest / 100 / 12), 2)
    # Calculates the final payment amount
    final_payment: float = round(np.add(current_credit_balance, interest_amount), 2)
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
    df_credit = pd.concat([df_credit, df_new_values], ignore_index=True)
    return df_credit


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


def run_credit_downpayment_plan_calculation(
    credit: float,
    interest: float,
    downpayment: float,
    currency: str = "EUR",
    language: str = "de",
) -> list:
    """
    Executes the calculation of a credit downpayment plan and generates a summary.
    This function calculates the monthly downpayment values for a given credit amount,
    interest rate, and repayment amount. It generates a detailed DataFrame of the
    downpayment plan and a summary DataFrame of the credit details. Both DataFrames
    are saved as CSV files.
    Args:
        credit (float): The initial credit amount.
        interest (float): The annual interest rate (in percentage).
        downpayment (float): The fixed monthly repayment amount.
        currency (str, optional): The currency of the credit. Defaults to "EUR".
    Raises:
        ValueError: If a required key is missing in the JSON configuration file.
    Notes:
        - The function uses a JSON configuration file to load text labels for column names.
        - The calculation continues until the remaining credit balance is less than the
          repayment amount, followed by a final payment calculation.
        - The resulting DataFrames are saved to CSV files with filenames specified in the
          JSON configuration.
    Returns:
        list: A list containing the summarized credit details, including:
        - credit amount (float)
        - interest rate (float)
        - duration (int)
        - monthly downpayment (float)
        - total interest (float)
        - total cost (float)
        - currency (str)
    """
    logger.info(f"Creating credit down payment plan for ({credit = })")

    # Load your text configuration
    output_text: dict = utils.load_text_json(
        language=language, interface="credit_simulation", filename="output_text"
    )

    # Validate and extract colum names
    plan_keys: list = [
        "duration",
        "remaining_credit",
        "interest_payment",
        "monthly_downpayment",
    ]
    try:
        col_names_simulation: list[str] = [output_text[key] for key in plan_keys]
        logger.debug(f"Resolved column names: {col_names_simulation}")
    except KeyError as e:
        msg = f"Missing expected key in JSON: {e}"
        logger.error(msg)
        raise ValueError

    # Create DataFrame
    df_credit_simulation = pd.DataFrame(
        data=[[0, credit, 0, 0]], columns=col_names_simulation
    )
    logger.debug(f"DataFrame created:\n{df_credit_simulation.head()}")

    # Calculate the monthly downpayment values until the remaining credit balance is less than the repayment amount
    # The last row of the DataFrame is used to check if the remaining credit balance is greater than the repayment amount
    print("...")
    while df_credit_simulation.iloc[-1][col_names_simulation[1]] > downpayment:
        df_credit_simulation = _calculate_monthly_downpayment(
            df_credit=df_credit_simulation,
            col_names=col_names_simulation,
            interest=interest,
            repayment=downpayment,
        )
        logger.debug(f"Updated DataFrame:\n{df_credit_simulation.tail()}")
    # Calculate the final payment
    df_credit_simulation = _calculate_final_downpayment(
        df_credit=df_credit_simulation,
        col_names=col_names_simulation,
        interest=interest,
    )
    logger.debug(f"Final DataFrame:\n{df_credit_simulation.tail()}")

    # Summary of the credit details
    # Validate and extract colum names for the summary
    plan_keys = [
        "credit_amount",  # 0 (float)
        "interest_rate",  # 1 (float)
        "duration",  # 2 (int)
        "monthly_downpayment",  # 3 (float)
        "total_interest",  # 4 (float)
        "total_cost",  # 5 (float)
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
    df_credit_summary = pd.DataFrame(
        data=[
            [
                credit,
                interest,
                df_credit_simulation.iloc[-1][col_names_simulation[0]],
                downpayment,
                df_credit_simulation[col_names_simulation[2]].sum().round(2),
                df_credit_simulation[col_names_simulation[2]].sum().round(2) + credit,
                currency,
            ]
        ],
        columns=col_names_summary,
    )
    df_credit_summary = df_credit_summary.astype({col_names_summary[2]: int})

    # Save the DataFrames to CSV files
    utils.save_dataframe_to_csv(
        df=df_credit_simulation, filename=output_text["file_name_credit_simulation"]
    )
    utils.save_dataframe_to_csv(
        df=df_credit_summary, filename=output_text["file_name_credit_summary"]
    )

    return df_credit_summary.iloc[0].values.tolist()


def calculate_monthly_payment_from_duration(
    credit_amount: float, annual_interest_rate: float, duration_months: int
) -> float:
    """
    Calculate the fixed monthly payment for a loan using the annuity formula.

    Args:
        credit_amount (float): Total loan amount (principal).
        annual_interest_rate (float): Annual interest rate (e.g., 5 for 5%).
        duration_months (int): Loan term in months.

    Returns:
        float: Monthly payment amount.
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
    monthly_payment = credit_amount * (numerator / denominator)

    return round(monthly_payment, 2)  # Round to 2 decimal places (cents)


def execute_simulation(language: str = "de", currency: str = "EUR") -> None:
    """
    Execute the credit simulation process.
    This function handles the credit simulation workflow, including user input,
    calculation of credit repayment plans, and displaying the results. It supports
    different languages and currencies.
    Args:
        language (str): The language code for the user interface text (default is "de").
        currency (str): The currency code for displaying monetary values (default is "EUR").
    Workflow:
        1. Load user interface text based on the selected language.
        2. Display welcome messages and currency information.
        3. Prompt the user to select a calculation method:
            - Option 0: Calculate based on a fixed monthly downpayment.
            - Option 1: Calculate based on a fixed credit duration.
        4. Collect necessary inputs from the user (e.g., credit amount, interest rate).
        5. Perform the selected calculation and generate a repayment summary.
        6. Display the summary of the credit details.
        7. Wait for user input to return to the homescreen.
    Notes:
        - The function clears the console screen before displaying the summary.
        - If no calculation is performed, an error is logged, and the function exits.
    Raises:
        ValueError: If invalid inputs are provided during user input prompts.
    Returns:
        None
    """
    logger.info("Executing the credit simulation")
    
    ui_text: dict = utils.load_text_json(
        language=language, interface="credit_simulation", filename="ui_text"
    )
    for dialog in ui_text["welcome_text"].values():
        print(dialog)
    print(f"{currency}")
    calculation_selection: int = _calculation_selection(ui_text)

    credit_amount: float = utils.user_input_float(
        ui_text["credit_amount"], ui_text["invalid_input"]
    )
    interest_rate: float = utils.user_input_float(
        ui_text["credit_interest_rate"], ui_text["invalid_input"]
    )

    summary: list = []
    downpayment: float

    if calculation_selection == 0:
        downpayment = _input_downpayment_monthly(
            credit=credit_amount,
            interest=interest_rate,
            ui_text=ui_text,
            currency=currency,
        )
    elif calculation_selection == 1:
        duration: int = utils.user_input_int(
            ui_text["credit_duration"], ui_text["invalid_input"]
        )
        downpayment = calculate_monthly_payment_from_duration(
            credit_amount=credit_amount,
            annual_interest_rate=interest_rate,
            duration_months=duration,
        )
    # Execute the credit downpayment plan calculation
    summary = run_credit_downpayment_plan_calculation(
        credit_amount, interest_rate, downpayment, currency, language
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
    logging.info("User returned to the homescreen after successfull credit simulation.")
    return
