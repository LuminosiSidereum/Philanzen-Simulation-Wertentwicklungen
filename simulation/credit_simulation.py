import pandas as pd  # type: ignore
import numpy as np
import utils


def _input_downpayment_monthly(credit: float, interest: float, ui_text: dict, currency: str = "EUR") -> float:
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
            print(f"{ui_text["credit_interest_monthly"]}: {interest_amount:.2f} {currency}")
            print(f"{ui_text["credit_downpayment_monthly"]}: {repayment:.2f} {currency}")
        else:
            return repayment


def _credit_downpayment_calculation(
    credit: float, interest: float, repayment: float
) -> tuple[float, float]:
    interest_amount: float = credit * (interest / 100 / 12)
    remaining_credit_balance: float = np.subtract(
        np.add(credit, interest_amount), repayment
    )
    return remaining_credit_balance, interest_amount


def _restzahlung(Kreditbetrag: float, Zinssatz: float) -> tuple[float, float]:
    Zinsen: float = Kreditbetrag * (Zinssatz / 100 / 12)
    Rückzahlung: float = np.add(Kreditbetrag, Zinsen)
    return Zinsen, Rückzahlung


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


def execute_simulation(language: str = "de", currency: str = "EUR") -> None:
    """
    Execute the credit simulation.
    """
    ui_text: dict = utils.load_ui_text(language=language, interface="credit_simulation")
    for dialog in ui_text["welcome_text"].values():
        print(dialog)
    print(f"{currency}")
    calculation_selection: int = _calculation_selection(ui_text)

    creit_amout: float = utils.user_input_float(
        ui_text["credit_amount"], ui_text["invalid_input"]
    )
    interest_rate: float = utils.user_input_float(
        ui_text["credit_interest_rate"], ui_text["invalid_input"]
    )

    if calculation_selection == 0:
        downpayment: float = _input_downpayment_monthly(
            credit=creit_amout, interest=interest_rate, ui_text=ui_text, currency=currency
        )
    elif calculation_selection == 1:
        duration: int = utils.user_input_int(
            ui_text["credit_duration"], ui_text["invalid_input"]
        )


if __name__ == "__main__":
    Zinsen: float
    Rückzahlung: float
    neuerKreditbetrag: float

    # Daten einlesen
    df_creditdetails = pd.read_csv("data/input/creditdetails.csv")
    df_creditdaten = pd.DataFrame(
        columns=["Laufzeit", "Kreditbetrag", "Rückzahlung", "Zinsertrag"]
    )

    if df_creditdetails.iloc[0]["Kreditbetrag"] > 0:
        speicherserie = pd.Series(
            {
                "Laufzeit": 0,
                "Kreditbetrag": df_creditdetails.iloc[0]["Kreditbetrag"],
                "Rückzahlung": 0,
                "Zinsertrag": 0,
            }
        )
        df_creditdaten = pd.concat([df_creditdaten, speicherserie.to_frame().T])
    while (
        df_creditdaten.iloc[-1]["Kreditbetrag"]
        - df_creditdetails.iloc[0]["Rückzahlung"]
        > 0
    ):
        neuerKreditbetrag, Zinsen = _input_downpayment_monthly(
            df_creditdaten.iloc[-1]["Kreditbetrag"],
            df_creditdetails.iloc[-1]["Zinssatz"],
            df_creditdetails.iloc[-1]["Rückzahlung"],
        )
        speicherserie = pd.Series(
            {
                "Laufzeit": df_creditdaten.iloc[-1]["Laufzeit"] + 1,
                "Kreditbetrag": neuerKreditbetrag,
                "Rückzahlung": df_creditdetails.iloc[-1]["Rückzahlung"],
                "Zinsertrag": Zinsen,
            }
        )
        df_creditdaten = pd.concat([df_creditdaten, speicherserie.to_frame().T])

    # Restzahlung berechnen
    Zinsen, Rückzahlung = _restzahlung(
        df_creditdaten.iloc[-1]["Kreditbetrag"], df_creditdetails.iloc[-1]["Zinssatz"]
    )
    speicherserie = pd.Series(
        {
            "Laufzeit": df_creditdaten.iloc[-1]["Laufzeit"] + 1,
            "Kreditbetrag": 0,
            "Rückzahlung": Rückzahlung,
            "Zinsertrag": Zinsen,
        }
    )
    df_creditdaten = pd.concat([df_creditdaten, speicherserie.to_frame().T])

    # Auswertung der Kreditdaten
    df_credituebersicht = pd.DataFrame(
        columns=["GesamtLaufzeit", "GeleisteteZahlungen", "Zinsertrag"]
    )
    gesamtlaufzeit: float = df_creditdaten.iloc[-1]["Laufzeit"]
    geleistetezahlungen: float = df_creditdaten["Rückzahlung"].sum()
    zinsertrag: float = df_creditdaten["Zinsertrag"].sum()
    speicherserie = pd.Series(
        {
            "GesamtLaufzeit": gesamtlaufzeit,
            "GeleisteteZahlungen": geleistetezahlungen,
            "Zinsertrag": zinsertrag,
        }
    )
    df_credituebersicht = pd.concat([df_credituebersicht, speicherserie.to_frame().T])

    # Daten speichern
    df_creditdaten.to_csv("data/output/creditdaten.csv", index=False)
    df_credituebersicht.to_csv("data/output/credituebersicht.csv", index=False)
