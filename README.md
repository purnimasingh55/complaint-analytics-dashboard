# Consumer Complaint Classification & Monitoring Dashboard

An end-to-end mini project that simulates a consumer-complaint analytics
workflow: **synthetic data generation → text classification of complaint
narratives → interactive monitoring dashboard**.

Built to demonstrate the core skills required for data-driven complaint
monitoring and policy-support work (e.g., classification of complaint trends,
automated reporting, and interactive dashboards for management review).

---

## Why this project

Organisations that handle large volumes of consumer complaints need
systematic ways to:
1. Automatically classify incoming complaints into categories
2. Track volume trends and emerging issue patterns over time
3. Provide management with an interactive, real-time view of complaint data
   rather than static reports

This project builds a small but complete version of that pipeline.

## Project structure

```
complaint-analytics-dashboard/
├── data/
│   ├── generate_data.py       # generates the synthetic complaints dataset
│   └── complaints.csv         # generated dataset (created after running the script)
├── src/
│   └── train_classifier.py    # trains TF-IDF + Logistic Regression classifier
├── dashboard/
│   └── app.py                 # Streamlit + Plotly interactive dashboard
├── models/                    # trained model saved here (.joblib)
├── outputs/                   # classification report + confusion matrix
├── requirements.txt
├── .gitignore
└── README.md
```

## About the data

The dataset (`data/complaints.csv`) is **synthetically generated**
(`data/generate_data.py`) to mirror realistic consumer-banking complaint
categories (Fraud/Unauthorized Transactions, ATM/Card Issues, Loan/Credit,
Account Opening/KYC, Digital Banking/UPI, Customer Service, Charges/Fees),
with realistic-sounding narratives, dates, states, channels, and resolution
outcomes.

**Honest note on model accuracy:** because the narratives are built from a
limited set of templates, the classifier achieves ~100% test accuracy — this
is an artifact of template repetition, not a claim about real-world
performance. On real, more varied complaint text, accuracy would be
meaningfully lower.

---

## Setup & running locally

**1. Clone / open the project folder, then create a virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Generate the dataset:**
```bash
python data/generate_data.py
```
This creates `data/complaints.csv` (~3,000 records).

**4. Train the classifier:**
```bash
python src/train_classifier.py
```
This prints accuracy/classification report to the console and saves:
- `models/complaint_classifier.joblib` (trained model)
- `outputs/classification_report.txt`
- `outputs/confusion_matrix.csv`

**5. Launch the dashboard:**
```bash
streamlit run dashboard/app.py
```
This opens the dashboard in your browser at `http://localhost:8501`.

---