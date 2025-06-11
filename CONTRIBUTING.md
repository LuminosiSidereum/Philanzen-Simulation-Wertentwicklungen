# Contribution Guidelines for Simulationen-Wertentwicklung

## 📌 General Rules
- **English is the standard language** for all **code, comments, variable names, function names, project documentation, Git commits, and discussions**.
- **German is used only for documentation aimed at customers** (e.g., user manuals and external guides), which will be edited separately and included in the customer package.
- Ensure **consistent formatting** and follow the naming conventions below.

---

## 📌 1️⃣ Naming Conventions

### **Variables & Attributes**
- Use **`snake_case`** for variables and attributes.
- ✅ **Good:** `monthly_interest_rate = 0.05`
- ❌ **Bad:** `MonthlyInterestRate = 0.05`

### **Functions & Methods**
- Use **`snake_case`** for function and method names.
- ✅ **Good:**
  ```python
  def calculate_monthly_interest(amount, rate):
      return amount * rate
  ```
- ❌ **Bad:** `def CalculateMonthlyInterest(Amount, Rate):`

### **Classes**
- Use **`CamelCase`** (PascalCase) for class names.
- ✅ **Good:**
  ```python
  class CreditSimulation:
      pass
  ```
- ❌ **Bad:** `class credit_simulation:`

### **Constants**
- Use **`UPPER_CASE`** for constants.
- ✅ **Good:** `DEFAULT_INTEREST_RATE = 5.0`
- ❌ **Bad:** `defaultInterestRate = 5.0`

### **Module & File Names**
- Use **`snake_case`** for Python files and modules.
- ✅ **Good:** `financial_simulation.py`
- ❌ **Bad:** `FinancialSimulation.py`

---

## 📌 2️⃣ Git Commit Message Format
- Keep messages clear and concise using present tense.
- Follow this format: `type: description`
- Types:
  - `feat:` → New features
  - `fix:` → Bug fixes
  - `docs:` → Documentation updates
  - `refactor:` → Code improvements without new features
  - `style:` → Code formatting changes (e.g., applying Black, indentation updates)
  - `chore:` → Changes to project files (e.g., README.md, CONTRIBUTING.md, or documentation updates)
  - `merge:` → Merge commits
  - `test:` → Adding or modifying tests

✅ **Good Examples:**
```
feat: add credit repayment simulation
fix: correct inflation rate calculation
style: reformat codebase with Black
chore: update README with new installation instructions
```
❌ **Bad Examples:**
```
added new feature for credit simulation
fixing bug in interest calculation
```

---

## 📌 3️⃣ Project Structure
```
Philanzen-Simulation-Wertentwicklung/
│── simulation/
│   │── __init__.py
│   │── credit_simulation.py
│   │── inflation_model.py
│   │── savings_calculation.py
│   │── utils.py
│   │── wealth_projection.py
│── resources/
│   │── folder_icon_philanzen.ico
│   │── output_text.json
│   │── settings.json
│   │── ui_text.json
│── main.py
│── README.md  # (German for customers, packaged separately)
│── poetry.lock
│── pyproject.toml
│── docs/  # (German documentation for customers, packaged separately)
│── .gitignore
```

---

## 📌 4️⃣ Documentation & Code Comments
- Use **docstrings (`"""Triple Quotes"""`)** for functions and classes.
- ✅ **Example for a function:**
  ```python
  def calculate_interest(amount: float, rate: float) -> float:
      """
      Calculate interest based on amount and rate.

      :param amount: The principal amount
      :param rate: The interest rate (in decimal)
      :return: The calculated interest amount
      """
      return amount * rate
  ```

- ✅ **Example for a class:**
  ```python
  class CreditSimulation:
      """
      A class to simulate loan repayment calculations.
      """
  ```
- **Note:** Type annotations are recommended for clarity but are not required.

---

## 📌 5️⃣ Code Formatting
- Use **tabs for indentation** (instead of spaces).
- Use **Black** for automatic formatting.
- Keep **lines under 80 characters** for readability.

---

## 📌 6️⃣ Submitting a Contribution
1. **Fork the repository** and create a new branch.
2. Follow the **naming conventions** and **commit message format**.
3. Test your code before submitting a pull request (PR).
4. Open a **PR with a clear description** of your changes.

---

✅ Following these guidelines ensures **consistency, readability, and maintainability** across the project.
Thanks for contributing! 🚀
