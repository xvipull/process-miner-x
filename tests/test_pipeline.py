import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.pipeline import run


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/order_events.csv"


class PipelineTests(unittest.TestCase):
    def test_pipeline_cleans_and_loads_star_model(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = run(FIXTURE, root, "2025-02-16T00:00:00Z")
            self.assertEqual(result["accepted_rows"], 4)
            self.assertEqual(result["quarantined_rows"], 0)
            self.assertTrue(all(check["status"] == "PASS" for check in result["checks"]))
            db = sqlite3.connect(root / "data/analytics.db")
            self.assertEqual(db.execute("SELECT COUNT(*) FROM fact_process_event").fetchone()[0], 4)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM dim_case").fetchone()[0], 2)
            self.assertEqual(db.execute("SELECT ROUND(SUM(amount), 2) FROM fact_process_event").fetchone()[0], 3699.5)
            self.assertEqual(json.loads((root / "reports/data_quality_report.json").read_text())["raw_rows"], 4)

    def test_bad_amount_is_quarantined(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "bad.csv"
            input_path.write_text(FIXTURE.read_text().replace('"$1,200.00"', '-10'), encoding="utf-8")
            result = run(input_path, Path(directory) / "output", "2025-02-16T00:00:00Z")
            self.assertEqual(result["accepted_rows"], 3)
            self.assertEqual(result["quarantined_rows"], 1)
            self.assertEqual(next(x for x in result["checks"] if x["name"] == "invalid_amount_range")["status"], "FAIL")

    def test_duplicate_event_is_quarantined_before_model_load(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "duplicate.csv"
            rows = FIXTURE.read_text(encoding="utf-8").splitlines()
            input_path.write_text("\n".join(rows + [rows[1]]) + "\n", encoding="utf-8")
            result = run(input_path, Path(directory) / "output", "2025-02-16T00:00:00Z")
            self.assertEqual(result["accepted_rows"], 4)
            self.assertEqual(result["quarantined_rows"], 1)
            self.assertEqual(next(x for x in result["checks"] if x["name"] == "duplicate_event_id")["observed"], 1)


if __name__ == "__main__":
    unittest.main()
