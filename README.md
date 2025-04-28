# Philanzen Financial Simulations

A Python CLI tool for personal finance simulations, including credit repayment planning, inflation modeling, savings projections, and wealth growth calculations.

## ✨ Features
- **Credit Simulation**: Calculate repayment plans with fixed monthly payments or target durations.
- **Inflation Model**: Project future purchasing power based on inflation rates.
- **Savings Plan**: Simulate savings growth with compound interest.
- **Wealth Projection**: Forecast long-term wealth with automatic savings adjustments.
- **Multi-language UI**: German (`de`) support via JSON configs.
- **CSV Exports**: Save simulation results for further analysis.

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- [Poetry](https://python-poetry.org/) (dependency management)

### Installation
```bash
git clone https://github.com/LuminosiSidereum/Philanzen-Simulation-Wertentwicklungen.git philanzen-financial-simulations
cd philanzen-financial-simulations
poetry install  # Installs dependencies
```

### Usage
```bash
poetry run python main.py
```
Follow the interactive menu to select simulations:
1. Wealth Projection  
2. Credit Simulation  
3. Inflation Model  
4. Savings Plan  

Results are saved in `data/output/` as CSV files.

## 📊 Simulation Examples
### Credit Repayment
```text
[Credit Simulation]
Amount: €10,000 | Interest: 5% | Monthly Payment: €200
→ Duration: 5 years 4 months | Total Interest: €1,728.42
```

### Inflation Impact
```text
[Inflation Model]
Capital: €50,000 | Inflation: 2% | Period: 10 years
→ Future Value: €40,773.11 (Purchasing Power)
```

## 🔧 Configuration
Modify `resources/settings.json` to adjust:
- Default currency (`EUR`)
- Annual inflation rate (`3.0`)
- UI language (`de`)

## 📁 Data Flow
```mermaid
graph LR
    A[User Input] --> B[Simulation]
    B --> C[CSV Results]
    C --> D[data/output/]
```
## 📜 License
The project is publsihed under the MIT license.
For further information [checkout license](LICENSE.txt).