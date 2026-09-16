"""Reproducible event-log ingestion, data-quality validation, and SQLite star-model load.

Run: python src/pipeline.py --input data/raw/order_events.csv --as-of 2025-02-16T00:00:00Z
The input is read-only: clean and quarantined rows are written to data/staging/.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

REQUIRED = {"event_id", "case_id", "activity_name", "event_timestamp", "source_system"}
ALLOWED_SOURCES = {"ERP", "CRM", "WMS"}
ACTIVITY_ALIASES = {
    "order received": "Order Received", "receive order": "Order Received",
    "validate order": "Validate Order", "payment confirmed": "Payment Confirmed",
    "pick items": "Pick Items", "ship order": "Ship Order", "order shipped": "Ship Order",
    "deliver order": "Deliver Order", "order delivered": "Deliver Order",
}
CURRENCY_ALIASES = {"$": "USD", "US$": "USD", "₹": "INR", "€": "EUR"}
NULL_THRESHOLDS = {"case_id": 0.0, "activity_name": 0.01, "event_timestamp": 0.01, "source_system": 0.0}


@dataclass
class QualityResult:
    name: str
    status: str
    observed: Any
    threshold: Any
    detail: str


def parse_timestamp(value: str) -> str:
    value = value.strip().replace("Z", "+00:00")
    stamp = datetime.fromisoformat(value)
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    return stamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_amount(value: str) -> str:
    if not value or not value.strip():
        return ""
    normalized = re.sub(r"[^0-9.\-]", "", value.replace(",", ""))
    amount = Decimal(normalized).quantize(Decimal("0.01"))
    if not Decimal("0") <= amount <= Decimal("10000000"):
        raise ValueError("amount outside permitted range 0..10,000,000")
    return str(amount)


def clean_row(row: dict[str, str]) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    clean = {key: (value or "").strip() for key, value in row.items()}
    clean["event_id"] = clean.get("event_id", "").upper()
    clean["case_id"] = clean.get("case_id", "").upper()
    activity = clean.get("activity_name", "").lower()
    clean["activity_name"] = ACTIVITY_ALIASES.get(activity, " ".join(word.capitalize() for word in activity.split()))
    clean["source_system"] = clean.get("source_system", "").upper()
    clean["currency"] = CURRENCY_ALIASES.get(clean.get("currency", "").upper(), clean.get("currency", "").upper())
    clean["queue_or_team"] = " ".join(word.capitalize() for word in clean.get("queue_or_team", "").split())
    clean["region_or_channel"] = clean.get("region_or_channel", "").upper()
    for column in ("event_timestamp", "sla_due_timestamp"):
        if clean.get(column):
            try:
                clean[column] = parse_timestamp(clean[column])
            except ValueError:
                errors.append(f"invalid {column}")
    try:
        clean["amount"] = parse_amount(clean.get("amount", ""))
    except (InvalidOperation, ValueError):
        errors.append("invalid amount")
    for column in REQUIRED:
        if not clean.get(column):
            errors.append(f"missing {column}")
    if clean.get("source_system") and clean["source_system"] not in ALLOWED_SOURCES:
        errors.append("unknown source_system")
    return clean, errors


def quality_checks(raw: list[dict[str, str]], clean: list[dict[str, str]], rejected: list[dict[str, str]], as_of: datetime) -> list[QualityResult]:
    results: list[QualityResult] = []
    present = set(raw[0]) if raw else set()
    missing = sorted(REQUIRED - present)
    results.append(QualityResult("required_columns", "PASS" if not missing else "FAIL", missing or "all present", "all required", "Input contract validation"))
    for column, threshold in NULL_THRESHOLDS.items():
        rate = sum(not row.get(column, "").strip() for row in raw) / len(raw) if raw else 1.0
        results.append(QualityResult(f"null_rate_{column}", "PASS" if rate <= threshold else "FAIL", round(rate, 4), threshold, "Raw input null-rate threshold"))
    duplicates = sum("duplicate event_id" in row["_errors"] for row in rejected)
    results.append(QualityResult("duplicate_event_id", "PASS" if duplicates == 0 else "FAIL", duplicates, 0, "Duplicate business keys are quarantined after cleaning"))
    invalid = sum("invalid amount" in row["_errors"] for row in rejected)
    results.append(QualityResult("invalid_amount_range", "PASS" if invalid == 0 else "FAIL", invalid, 0, "Amount must be 0..10,000,000"))
    future = sum(datetime.fromisoformat(row["event_timestamp"].replace("Z", "+00:00")) > as_of for row in clean if row.get("event_timestamp"))
    results.append(QualityResult("future_event_timestamp", "PASS" if future == 0 else "FAIL", future, 0, "Event cannot be after run as-of timestamp"))
    latest = max((datetime.fromisoformat(row["event_timestamp"].replace("Z", "+00:00")) for row in clean if row.get("event_timestamp")), default=None)
    age_hours = round((as_of - latest).total_seconds() / 3600, 1) if latest else None
    results.append(QualityResult("freshness", "PASS" if age_hours is not None and age_hours <= 48 else "FAIL", age_hours, "<= 48 hours", "Age of newest accepted event"))
    source_failures = sum(row.get("source_system") not in ALLOWED_SOURCES for row in clean)
    results.append(QualityResult("source_system_reference", "PASS" if source_failures == 0 else "FAIL", source_failures, 0, "Source-system reference integrity"))
    results.append(QualityResult("row_reconciliation", "PASS" if len(raw) == len(clean) + len(rejected) else "FAIL", f"{len(raw)} = {len(clean)} + {len(rejected)}", "raw = accepted + rejected", "All source rows accounted for"))
    return results


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row} - {"_errors"}) or sorted(REQUIRED)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows([{k: v for k, v in row.items() if k != "_errors"} for row in rows])


def load_star_model(db_path: Path, rows: list[dict[str, str]]) -> dict[str, Any]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript("""
    DROP TABLE IF EXISTS fact_process_event; DROP TABLE IF EXISTS dim_case; DROP TABLE IF EXISTS dim_activity; DROP TABLE IF EXISTS dim_source_system; DROP TABLE IF EXISTS dim_date;
    CREATE TABLE dim_case (case_key INTEGER PRIMARY KEY, case_id TEXT NOT NULL UNIQUE, product_or_service TEXT, region_or_channel TEXT, customer_id TEXT);
    CREATE TABLE dim_activity (activity_key INTEGER PRIMARY KEY, activity_name TEXT NOT NULL UNIQUE);
    CREATE TABLE dim_source_system (source_system_key INTEGER PRIMARY KEY, source_system TEXT NOT NULL UNIQUE);
    CREATE TABLE dim_date (date_key INTEGER PRIMARY KEY, calendar_date TEXT NOT NULL UNIQUE, year INTEGER NOT NULL, month INTEGER NOT NULL, day INTEGER NOT NULL);
    CREATE TABLE fact_process_event (
      event_key INTEGER PRIMARY KEY, event_id TEXT NOT NULL UNIQUE, case_key INTEGER NOT NULL, activity_key INTEGER NOT NULL, source_system_key INTEGER NOT NULL, event_date_key INTEGER NOT NULL,
      event_timestamp TEXT NOT NULL, lifecycle TEXT, queue_or_team TEXT, amount REAL, currency TEXT, sla_due_timestamp TEXT,
      FOREIGN KEY(case_key) REFERENCES dim_case(case_key), FOREIGN KEY(activity_key) REFERENCES dim_activity(activity_key),
      FOREIGN KEY(source_system_key) REFERENCES dim_source_system(source_system_key), FOREIGN KEY(event_date_key) REFERENCES dim_date(date_key));
    """)
    def key(table: str, column: str, value: str, extras: tuple = ()) -> int:
        connection.execute(f"INSERT OR IGNORE INTO {table} ({column}) VALUES (?)", (value,))
        return connection.execute(f"SELECT {table.replace('dim_', '')}_key FROM {table} WHERE {column} = ?", (value,)).fetchone()[0]
    for row in rows:
        connection.execute("INSERT OR IGNORE INTO dim_case(case_id, product_or_service, region_or_channel, customer_id) VALUES (?, ?, ?, ?)", (row["case_id"], row.get("product_or_service"), row.get("region_or_channel"), row.get("customer_id")))
        case_key = connection.execute("SELECT case_key FROM dim_case WHERE case_id=?", (row["case_id"],)).fetchone()[0]
        activity_key = key("dim_activity", "activity_name", row["activity_name"])
        source_key = key("dim_source_system", "source_system", row["source_system"])
        date = row["event_timestamp"][:10]; date_key = int(date.replace("-", ""))
        connection.execute("INSERT OR IGNORE INTO dim_date VALUES (?, ?, ?, ?, ?)", (date_key, date, int(date[:4]), int(date[5:7]), int(date[8:10])))
        connection.execute("INSERT INTO fact_process_event(event_id,case_key,activity_key,source_system_key,event_date_key,event_timestamp,lifecycle,queue_or_team,amount,currency,sla_due_timestamp) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (row["event_id"], case_key, activity_key, source_key, date_key, row["event_timestamp"], row.get("event_lifecycle"), row.get("queue_or_team"), float(row["amount"]) if row.get("amount") else None, row.get("currency"), row.get("sla_due_timestamp")))
    connection.commit()
    counts = {table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in ("dim_case", "dim_activity", "dim_source_system", "dim_date", "fact_process_event")}
    amount = connection.execute("SELECT COALESCE(SUM(amount), 0) FROM fact_process_event").fetchone()[0]
    connection.close()
    return {"table_counts": counts, "fact_amount_total": round(amount, 2)}


def run(input_path: Path, root: Path, as_of: str | None = None) -> dict[str, Any]:
    with input_path.open(newline="", encoding="utf-8") as handle: raw = list(csv.DictReader(handle))
    clean, rejected, seen_event_ids = [], [], set()
    for row in raw:
        standardized, errors = clean_row(row)
        if not errors and standardized["event_id"] in seen_event_ids:
            errors.append("duplicate event_id")
        if errors:
            standardized["_errors"] = "; ".join(errors); rejected.append(standardized)
        else:
            seen_event_ids.add(standardized["event_id"])
            clean.append(standardized)
    as_of_dt = datetime.fromisoformat((as_of or datetime.now(timezone.utc).isoformat()).replace("Z", "+00:00"))
    results = quality_checks(raw, clean, rejected, as_of_dt)
    write_csv(root / "data/staging/clean_events.csv", clean); write_csv(root / "data/staging/quarantined_events.csv", rejected)
    model = load_star_model(root / "data/analytics.db", clean)
    report = {"input": str(input_path), "run_as_of": as_of_dt.isoformat(), "raw_rows": len(raw), "accepted_rows": len(clean), "quarantined_rows": len(rejected), "checks": [asdict(item) for item in results], "model": model}
    report_path = root / "reports/data_quality_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown = ["# Data Quality Report", "", f"- Input: `{input_path}`", f"- Run as of: `{as_of_dt.isoformat()}`", f"- Rows: {len(raw)} raw / {len(clean)} accepted / {len(rejected)} quarantined", "", "| Check | Status | Observed | Threshold |", "| --- | --- | --- | --- |"]
    markdown += [f"| {item.name} | {item.status} | {item.observed} | {item.threshold} |" for item in results]
    markdown += ["", "## Model reconciliation", "", f"Fact events: {model['table_counts']['fact_process_event']}; fact amount total: {model['fact_amount_total']}."]
    (root / "reports/data_quality_report.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--input", type=Path, required=True); parser.add_argument("--as-of")
    args = parser.parse_args(); result = run(args.input, Path(__file__).resolve().parents[1], args.as_of)
    print(json.dumps({"accepted_rows": result["accepted_rows"], "quarantined_rows": result["quarantined_rows"]}))
