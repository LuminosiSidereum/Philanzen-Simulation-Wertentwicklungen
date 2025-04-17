# **Key Formulas: Annuity Calculations**  
This document explains the core mathematical formulas used in the project for calculating **monthly payments** for loans and savings goals.  

---

## **1. Annuity Formula (Fixed Payments)**  
The formula calculates the fixed monthly payment ($P$) required to reach a future value (savings) or pay off a present value (loan) over a fixed period with compound interest.  

### **General Formula**  
$
P = \frac{A \times r}{(1 + r)^n - 1} \quad \text{(Savings)}  
$  
$
P = \frac{A \times r \times (1 + r)^n}{(1 + r)^n - 1} \quad \text{(Loans)}  
$  

Where:  
- $A$ = Target amount (`target_amount` or `credit_amount`).  
- $r$ = **Monthly interest rate** = `annual_interest_rate / 100 / 12`.  
- $n$ = **Total number of payments** = `duration_years * 12` or `duration_months`.  

### **Intuition**  
- **Savings**: The numerator ($A \times r$) scales the goal by the interest rate, while the denominator accounts for compounding over time.  
- **Loans**: The extra $(1 + r)^n$ factor adjusts for the decreasing principal over time (amortization).  

---

## **2. Edge Cases**  
### **Zero Interest ($r = 0$)**  
If interest is 0%, the formula simplifies to:  
$
P = \frac{A}{n}  
$  
Example: To save €12,000 in 12 months with 0% interest:  
$
P = \frac{12000}{12} = 1000 \ \text{€/month}  
$  

### **Validation Checks**  
- **Duration** must be positive ($n > 0$).  
- **Interest rate** cannot be negative ($r \geq 0$).  

---

## **3. Derivation (For Context)**  
The formula is derived from the **future value of an annuity** for savings:  
$
A = P \times \frac{(1 + r)^n - 1}{r}  
$  
Solving for $P$ gives the savings formula. For loans, it's derived from the **present value of an annuity**.  

---

## **4. Practical Example**  
### **Savings Goal**  
Goal: €100,000 in 5 years at 5% annual interest.  
- $r = 0.05 / 12 = 0.004167$  
- $n = 5 \times 12 = 60$  
$
P = \frac{100000 \times 0.004167}{(1 + 0.004167)^{60} - 1} = 1433.28 \ \text{€/month}  
$  

### **Loan Repayment**  
Loan: €300,000 over 30 years at 3.5% interest.  
- $r = 0.035 / 12 = 0.002917$  
- $n = 30 \times 12 = 360$  
$
P = \frac{300000 \times 0.002917 \times (1 + 0.002917)^{360}}{(1 + 0.002917)^{360} - 1} = 1347.13 \ \text{€/month}  
$  

---

## **5. References**  
- [Annuity (Finance Theory)](https://en.wikipedia.org/wiki/Annuity_(finance_theory))  
- [Time Value of Money](https://www.investopedia.com/terms/t/timevalueofmoney.asp)  
