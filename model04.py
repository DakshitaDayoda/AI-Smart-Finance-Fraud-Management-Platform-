import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# -----------------------------------
# 1. SYNTHETIC DATASET
# -----------------------------------
np.random.seed(42)

n = 3000

data = pd.DataFrame({
    "income": np.random.randint(20000, 200000, n),
    "loan_amount": np.random.randint(50000, 1500000, n),
    "interest_rate": np.random.uniform(5, 20, n),
    "tenure": np.random.randint(1, 30, n)
})

# -----------------------------------
# 2. EMI CALCULATION
# -----------------------------------
r = data["interest_rate"] / 12 / 100
n_months = data["tenure"] * 12

data["emi"] = (
    data["loan_amount"] *
    r *
    (1 + r) ** n_months
) / ((1 + r) ** n_months - 1)

# -----------------------------------
# 3. LABEL CREATION (RISK)
# -----------------------------------
# Rule: EMI > 40% of income => HIGH RISK
data["risk"] = np.where(data["emi"] > data["income"] * 0.4, 1, 0)

# 0 = Safe Loan
# 1 = High Risk Loan

# -----------------------------------
# 4. FEATURES & TARGET
# -----------------------------------
X = data[["income", "loan_amount", "interest_rate", "tenure", "emi"]]
y = data["risk"]

# -----------------------------------
# 5. TRAIN-TEST SPLIT
# -----------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -----------------------------------
# 6. MODEL TRAINING
# -----------------------------------
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

# -----------------------------------
# 7. PREDICTION & EVALUATION
# -----------------------------------
y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# -----------------------------------
# 8. SAVE MODEL
# -----------------------------------
joblib.dump(model, "loan_risk_model.pkl")

print("\nModel saved successfully as loan_risk_model.pkl")

# -----------------------------------
# Model testing code
# -----------------------------------

import joblib
import pandas as pd

model = joblib.load("loan_risk_model.pkl")

# Example input
sample = pd.DataFrame([[
    50000,   # income
    300000,  # loan_amount
    10,      # interest_rate
    5,       # tenure
    6500     # emi
]], columns=["income", "loan_amount", "interest_rate", "tenure", "emi"])

prediction = model.predict(sample)

if prediction[0] == 0:
    print("SAFE LOAN ✅")
else:
    print("HIGH RISK LOAN ❌")


# HIGH RISK INPUT
sample = pd.DataFrame([[
    30000,    # income (low)
    800000,   # loan_amount (high)
    15,       # interest_rate (high)
    20,       # tenure (long)
    15000     # emi (very high compared to income)
]], columns=["income", "loan_amount", "interest_rate", "tenure", "emi"])

prediction = model.predict(sample)

if prediction[0] == 0:
    print("SAFE LOAN ✅")
else:
    print("HIGH RISK LOAN ❌")