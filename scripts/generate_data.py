import csv
import random
from datetime import date, timedelta
from pathlib import Path

COUNT = 50_000
rng = random.Random(20260927)
selected = rng.sample(range(1, COUNT + 1), 650)

review_high = set(selected[:250])
benign_high = set(selected[250:400])
review_repeat = set(selected[400:550])
missing_provider = set(selected[550:650])

output = Path("data/generated")
output.mkdir(parents=True, exist_ok=True)

transactions = []
truth = []

for n in range(1, COUNT + 1):
    status = "REVERSED" if rng.random() < 0.02 else "PAID"
    amount = round(rng.uniform(20, 240), 2)
    scenario = "ROUTINE"

    if n in review_high:
        amount = round(rng.uniform(600, 850), 2)
        status, scenario = "PAID", "HIGH_AMOUNT_REVIEW"
    elif n in benign_high:
        amount = round(rng.uniform(500, 750), 2)
        status, scenario = "PAID", "BENIGN_HIGH_AMOUNT"
    elif n in review_repeat:
        status, scenario = "PAID", "REPEAT_FILL_REVIEW"
    elif n in missing_provider:
        scenario = "MISSING_PRESCRIBER"

    transaction = {
        "transaction_id": f"TXN2-{n:06d}",
        "transaction_date": date(2026, 1, 1) + timedelta(days=rng.randrange(180)),
        "pharmacy_id": f"PHARM-{rng.randint(1, 100):03d}",
        "patient_id": f"PAT-{rng.randint(1, 10000):05d}",
        "prescriber_id": (
            None if n in missing_provider
            else f"PROV-{rng.randint(1, 500):04d}"
        ),
        "drug_id": f"DRUG-{rng.randint(1, 80):03d}",
        "quantity": rng.randint(1, 90),
        "claim_amount": f"{amount:.2f}",
        "claim_status": status,
        "source_system": "SYNTHETIC_DEMO_V2",
    }
    transactions.append(transaction)
    truth.append({
        "transaction_id": transaction["transaction_id"],
        "scenario": scenario,
        "expected_review": int(
            scenario in {"HIGH_AMOUNT_REVIEW", "REPEAT_FILL_REVIEW"}
        ),
    })

routine_paid = [
    i for i, transaction in enumerate(transactions)
    if truth[i]["scenario"] == "ROUTINE"
    and transaction["claim_status"] == "PAID"
]

for n in review_repeat:
    base = transactions[rng.choice(routine_paid)]
    target = transactions[n - 1]
    for field in (
        "pharmacy_id", "patient_id", "prescriber_id",
        "drug_id", "quantity", "claim_amount"
    ):
        target[field] = base[field]
    target["transaction_date"] = base["transaction_date"] + timedelta(days=1)


def write_csv(path, records):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)


write_csv(output / "pharmacy_transactions_v2.csv", transactions)
write_csv(output / "ground_truth_v2.csv", truth)

assert len(transactions) == COUNT
assert sum(row["expected_review"] for row in truth) == 400
print("Generated 50,000 transactions; 400 labeled review cases.")