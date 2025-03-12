import pandas as pd  # type: ignore
import numpy as np


def _kreditberechnung(
    Kreditbetrag: float, Zinssatz: float, Rückzahlung: float
) -> tuple[float, float]:
    Zinsen: float = Kreditbetrag * (Zinssatz / 100 / 12)
    if Zinsen > Rückzahlung:
        print(
            f"Rückzahlung reicht nicht aus, um die Zinsen von {Zinsen:.2f}€ zu decken."
        )
        print(
            f"Bitte erhöhen Sie die Rückzahlung so, dass diese über den Zinsen liegt."
        )
        quit()
    neuerKreditbetrag: float = np.subtract(np.add(Kreditbetrag, Zinsen), Rückzahlung)
    return neuerKreditbetrag, Zinsen


def _restzahlung(Kreditbetrag: float, Zinssatz: float) -> tuple[float, float]:
    Zinsen: float = Kreditbetrag * (Zinssatz / 100 / 12)
    Rückzahlung: float = np.add(Kreditbetrag, Zinsen)
    return Zinsen, Rückzahlung


if __name__ == "__main__":
    Zinsen: float
    Rückzahlung: float
    neuerKreditbetrag: float

    # Daten einlesen
    df_creditdetails = pd.read_csv("data/creditdetails.csv")
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
        neuerKreditbetrag, Zinsen = _kreditberechnung(
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
    df_creditdaten.to_csv("data/creditdaten.csv", index=False)
    df_credituebersicht.to_csv("data/credituebersicht.csv", index=False)
