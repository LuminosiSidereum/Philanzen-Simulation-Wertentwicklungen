from simulation import credit_simulation, wealth_projection


def main():
    print("Welche Simulation möchten Sie starten?")
    print("1: Vermögensentwicklung")
    print("2: Abzahlungsplan")
    print("3: Inflationssimulation")
    print("3: Sparplan")

    user_choice = input("Bitte Nummer eingeben: ")

    if user_choice == "1":
        wealth_projection.execute_simulation()
    elif user_choice == "2":
        credit_simulation.execute_simulation()
    elif user_choice == "3":
        pass
    elif user_choice == "4":
        pass
    else:
        print("Ungültige Auswahl.")


if __name__ == "__main__":
    main()
