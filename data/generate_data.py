import random
import csv
from datetime import date, timedelta

random.seed(42)

# ---------------------------------------------------------------------------
# 1. Complaint categories + vocabulary bank for each category
#    (category, [subject templates], [detail phrases])
# ---------------------------------------------------------------------------

CATEGORIES = {
    "Fraud / Unauthorized Transactions": {
        "subjects": [
            "Unauthorized debit of Rs {amt} from my account",
            "Fraudulent transaction on my {card} card",
            "Money debited without my consent",
            "OTP fraud - amount deducted without authorization",
            "Phishing call led to unauthorized transfer",
        ],
        "details": [
            "I received a call from an unknown number claiming to be from the bank and my account was debited by Rs {amt} without my authorization.",
            "I noticed an unauthorized transaction of Rs {amt} on my {card} card statement which I did not perform.",
            "Someone used my UPI ID to transfer Rs {amt} without my knowledge or consent.",
            "My account was compromised and Rs {amt} was withdrawn through an ATM I never visited.",
            "I did not share my OTP with anyone yet Rs {amt} was debited from my savings account.",
        ],
    },
    "ATM / Card Issues": {
        "subjects": [
            "ATM did not dispense cash but amount debited",
            "Card blocked without any prior notice",
            "Duplicate card charges applied",
            "ATM swallowed my debit card",
            "Card declined despite sufficient balance",
        ],
        "details": [
            "I attempted to withdraw Rs {amt} from an ATM but cash was not dispensed, yet my account was debited.",
            "My {card} card was blocked suddenly and I was not informed of the reason despite calling customer care.",
            "I was charged twice for a single annual card fee this quarter.",
            "The ATM machine retained my card and I have not received it back after multiple visits to the branch.",
            "My card transaction was declined at a merchant outlet even though I had sufficient balance in my account.",
        ],
    },
    "Loan / Credit": {
        "subjects": [
            "Incorrect interest calculation on my loan account",
            "Loan foreclosure charges not disclosed",
            "EMI deducted twice in the same month",
            "Delay in loan disbursement",
            "Credit score impacted due to incorrect reporting",
        ],
        "details": [
            "The interest charged on my loan account does not match the amortization schedule shared at the time of sanction.",
            "I was charged foreclosure charges of Rs {amt} that were never explained to me when I took the loan.",
            "My EMI of Rs {amt} was deducted twice from my account in the same billing cycle.",
            "There has been an unexplained delay of over a month in disbursement of my sanctioned loan amount.",
            "My credit score has been negatively impacted due to incorrect reporting of my loan repayment status.",
        ],
    },
    "Account Opening / KYC": {
        "subjects": [
            "Account not activated despite KYC completion",
            "Repeated requests for KYC documents already submitted",
            "Account frozen due to KYC mismatch",
            "Delay in re-KYC process",
            "Nominee details not updated despite request",
        ],
        "details": [
            "I completed my KYC formalities over three weeks ago but my account is still not activated.",
            "The branch keeps asking for documents that I have already submitted twice for KYC verification.",
            "My account has been frozen citing a KYC mismatch even though my documents are valid and up to date.",
            "My re-KYC request submitted online has not been processed for over a month.",
            "Despite submitting the nominee update form, the nominee details on my account remain unchanged.",
        ],
    },
    "Digital Banking / UPI": {
        "subjects": [
            "UPI transaction failed but amount debited",
            "Mobile banking app not reflecting correct balance",
            "Unable to reset net banking password",
            "Fund transfer stuck in pending status",
            "UPI autopay deducted incorrect amount",
        ],
        "details": [
            "My UPI transaction of Rs {amt} failed on the app but the amount was debited from my account and not reversed.",
            "The mobile banking app is showing an incorrect balance that does not match my passbook entries.",
            "I am unable to reset my net banking password despite following the official reset procedure multiple times.",
            "A fund transfer of Rs {amt} initiated three days ago is still showing as pending status.",
            "My UPI autopay mandate deducted Rs {amt} which is more than the agreed subscription amount.",
        ],
    },
    "Customer Service": {
        "subjects": [
            "No response from customer care for over a week",
            "Branch staff misbehavior during visit",
            "Complaint ticket closed without resolution",
            "Long waiting time for grievance redressal",
            "Unable to reach relationship manager",
        ],
        "details": [
            "I have called customer care multiple times over the past week regarding my issue but have received no response.",
            "I was treated rudely by the branch staff when I visited to resolve my account issue.",
            "My previous complaint ticket was closed by the bank without actually resolving the underlying issue.",
            "It has been over 20 days since I raised this grievance and there has been no update on the resolution.",
            "I have been unable to reach my assigned relationship manager despite repeated attempts.",
        ],
    },
    "Charges / Fees": {
        "subjects": [
            "Unexplained deduction of maintenance charges",
            "SMS alert charges billed incorrectly",
            "Minimum balance penalty despite maintaining balance",
            "Hidden charges on account statement",
            "Excess GST charged on banking fees",
        ],
        "details": [
            "I was charged Rs {amt} as account maintenance charges without prior intimation.",
            "SMS alert charges of Rs {amt} were deducted even though I have not used the SMS alert facility.",
            "I was charged a minimum balance penalty despite maintaining the required average monthly balance.",
            "My account statement shows multiple charges of Rs {amt} that were never explained to me.",
            "The GST charged on my banking fees this month is higher than the applicable rate.",
        ],
    },
}

STATES = [
    "Uttar Pradesh", "Maharashtra", "Delhi", "Karnataka", "Tamil Nadu",
    "West Bengal", "Gujarat", "Rajasthan", "Madhya Pradesh", "Bihar",
    "Telangana", "Kerala", "Punjab", "Haryana", "Odisha",
]

CARD_TYPES = ["debit", "credit", "RuPay debit", "prepaid"]

STATUSES = ["Resolved", "Pending", "Escalated", "Closed - No Action"]
# Weighted so most complaints resolve, mirroring real-world distributions
STATUS_WEIGHTS = [0.62, 0.16, 0.12, 0.10]


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def generate_row(complaint_id: int) -> dict:
    category = random.choice(list(CATEGORIES.keys()))
    bank_info = CATEGORIES[category]
    amt = random.choice([500, 1200, 2500, 3000, 4999, 7500, 10000, 15000, 25000, 50000])
    card = random.choice(CARD_TYPES)

    subject = random.choice(bank_info["subjects"]).format(amt=amt, card=card)
    detail = random.choice(bank_info["details"]).format(amt=amt, card=card)
    narrative = f"{subject}. {detail}"

    complaint_date = random_date(date(2025, 1, 1), date(2026, 6, 30))
    status = random.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0]

    if status in ("Resolved", "Closed - No Action"):
        resolution_days = max(1, int(random.gauss(9, 6)))
    else:
        resolution_days = ""  # not yet resolved

    return {
        "complaint_id": f"C{complaint_id:06d}",
        "date_filed": complaint_date.isoformat(),
        "category": category,
        "narrative": narrative,
        "state": random.choice(STATES),
        "channel": random.choice(["Mobile App", "Branch", "Call Centre", "Email", "Website"]),
        "status": status,
        "resolution_days": resolution_days,
    }


def main(n_rows: int = 3000, out_path: str = "data/complaints.csv"):
    rows = [generate_row(i + 1) for i in range(n_rows)]
    fieldnames = list(rows[0].keys())
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {n_rows} synthetic complaint records -> {out_path}")


if __name__ == "__main__":
    main()
