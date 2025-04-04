import pandas as pd  # type: ignore


def _vermögensberechnung(Vermoegen, Zinssatz, Sparrate) -> tuple[float, float]:
    Zinsen = Vermoegen * (Zinssatz / 100 / 12)
    neuerKreditbetrag = Vermoegen + Zinsen + Sparrate
    return neuerKreditbetrag, Zinsen


if __name__ == "__main__":
    # Daten einlesen
    df_ertragsdetails = pd.read_csv("data/input/ertragsdetails.csv")
    df_vermoegensdaten = pd.DataFrame(
        columns=["Laufzeit", "Vermögen", "Sparrate", "Zinsertrag"]
    )

    if df_ertragsdetails.iloc[0]["Startkapital"] > 0:
        speicherserie = pd.Series(
            {
                "Laufzeit": 0,
                "Vermögen": df_ertragsdetails.iloc[0]["Startkapital"],
                "Sparrate": 0,
                "Zinsertrag": 0,
            }
        )
        df_vermoegensdaten = pd.concat([df_vermoegensdaten, speicherserie.to_frame().T])
    else:
        speicherserie = pd.Series(
            {"Laufzeit": 0, "Vermögen": 0, "Sparrate": 0, "Zinsertrag": 0}
        )
        df_vermoegensdaten = pd.concat([df_vermoegensdaten, speicherserie.to_frame().T])

    Sparrate = df_ertragsdetails.iloc[-1]["Sparrate"]
    for Monat in range(1, df_ertragsdetails.iloc[-1]["Laufzeit"] + 1):
        if Monat % 12 == 0:
            Sparrate = Sparrate * (
                1 + (df_ertragsdetails.iloc[-1]["Sparratenanpassung"] / 100)
            )

        neuesVermoegen, Zinsen = _vermögensberechnung(
            df_vermoegensdaten.iloc[-1]["Vermögen"],
            df_ertragsdetails.iloc[-1]["Zinssatz"],
            Sparrate,
        )
        speicherserie = pd.Series(
            {
                "Laufzeit": Monat,
                "Vermögen": neuesVermoegen,
                "Sparrate": Sparrate,
                "Zinsertrag": Zinsen,
            }
        )
        df_vermoegensdaten = pd.concat([df_vermoegensdaten, speicherserie.to_frame().T])

    # Auswertung der Kreditdaten
    df_credituebersicht = pd.DataFrame(
        columns=[
            "GesamtLaufzeit",
            "GesamtVermögen",
            "InflationsbereinigteKaufkraft",
            "GeleisteteZahlungen",
            "Zinsertrag",
        ]
    )
    gesamtlaufzeit = df_vermoegensdaten.iloc[-1]["Laufzeit"]
    gesamtvermoegen = df_vermoegensdaten.iloc[-1]["Vermögen"]
    inflationsbereinigteKaufkraft = gesamtvermoegen / (
        (1 + df_ertragsdetails.iloc[-1]["Inflationsrate"] / 100)
        ** (gesamtlaufzeit / 12)
    )
    geleistetezahlungen = df_vermoegensdaten["Sparrate"].sum()
    zinsertrag = df_vermoegensdaten["Zinsertrag"].sum()
    speicherserie = pd.Series(
        {
            "GesamtLaufzeit": gesamtlaufzeit,
            "GesamtVermögen": gesamtvermoegen,
            "InflationsbereinigteKaufkraft": inflationsbereinigteKaufkraft,
            "GeleisteteZahlungen": geleistetezahlungen,
            "Zinsertrag": zinsertrag,
        }
    )
    df_credituebersicht = pd.concat([df_credituebersicht, speicherserie.to_frame().T])

    # Daten speichern
    df_vermoegensdaten.to_csv("data/output/vermoegensdaten.csv", index=False)
    df_credituebersicht.to_csv("data/output/vermoegensuebersicht.csv", index=False)
