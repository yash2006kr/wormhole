"""
ApplyCopilot Idempotency Sentinel & Write-Ahead Transaction Ledger (WAL).
Prevents duplicate payments/submissions after abrupt browser or system crashes.
"""

import json
import os
import time
import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LEDGER_FILE = BASE_DIR / "transaction_ledger.json"

class TransactionLedger:
    def __init__(self, ledger_path=LEDGER_FILE):
        self.ledger_path = ledger_path
        self._ensure_ledger()

    def _ensure_ledger(self):
        if not self.ledger_path.exists():
            self._save_ledger({"transactions": []})

    def _load_ledger(self):
        try:
            if self.ledger_path.exists():
                return json.loads(self.ledger_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[LEDGER ERROR] Loading ledger failed: {e}")
        return {"transactions": []}

    def _save_ledger(self, data):
        try:
            self.ledger_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"[LEDGER ERROR] Saving ledger failed: {e}")

    def compute_idempotency_key(self, url, selector, amount):
        clean_url = url.split("?")[0].rstrip("/")
        raw = f"{clean_url}:{selector}:{amount}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def record_in_flight(self, url, selector, action_type="click", amount=0.0, currency="INR", order_id="", goal=""):
        """
        Write-Ahead Log (WAL): Persists an irreversible transaction intent BEFORE executing.
        Status: IN_FLIGHT_SUBMITTED.
        """
        ledger = self._load_ledger()
        tx_id = f"TX-{int(time.time() * 1000)}"
        idempotency_key = self.compute_idempotency_key(url, selector, amount)

        entry = {
            "tx_id": tx_id,
            "idempotency_key": idempotency_key,
            "status": "IN_FLIGHT_SUBMITTED",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "url": url,
            "selector": selector,
            "action_type": action_type,
            "amount": amount,
            "currency": currency,
            "order_id": order_id,
            "goal": goal,
            "reconciled": False,
            "reconciliation_notes": ""
        }

        ledger["transactions"].append(entry)
        self._save_ledger(ledger)
        print(f"[LEDGER WAL] In-flight transaction recorded: {tx_id} ({currency} {amount}) on {selector}")
        return entry

    def mark_settled(self, tx_id, receipt_info=""):
        """Marks a transaction as successfully completed and confirmed."""
        ledger = self._load_ledger()
        for tx in ledger.get("transactions", []):
            if tx.get("tx_id") == tx_id:
                tx["status"] = "SETTLED"
                tx["reconciled"] = True
                tx["receipt"] = receipt_info
                tx["settled_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
                self._save_ledger(ledger)
                print(f"[LEDGER WAL] Transaction {tx_id} marked as SETTLED.")
                return tx
        return None

    def get_pending_in_flight(self):
        """Returns any transactions that were submitted but never confirmed (i.e. browser crashed)."""
        ledger = self._load_ledger()
        pending = []
        for tx in ledger.get("transactions", []):
            if tx.get("status") == "IN_FLIGHT_SUBMITTED":
                pending.append(tx)
        return pending

    def is_duplicate_submission(self, url, selector, amount, window_seconds=600):
        """Checks if an identical transaction was submitted recently to prevent double charging."""
        ledger = self._load_ledger()
        target_key = self.compute_idempotency_key(url, selector, amount)
        now = time.time()
        for tx in reversed(ledger.get("transactions", [])):
            if tx.get("idempotency_key") == target_key:
                # Check status
                if tx.get("status") in ["IN_FLIGHT_SUBMITTED", "SETTLED"]:
                    return True, tx
        return False, None

    def reconcile_and_close(self, tx_id, status="RECONCILED_SUCCESS", notes=""):
        ledger = self._load_ledger()
        for tx in ledger.get("transactions", []):
            if tx.get("tx_id") == tx_id:
                tx["status"] = status
                tx["reconciled"] = True
                tx["reconciliation_notes"] = notes
                tx["reconciled_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
                self._save_ledger(ledger)
                return tx
        return None

# Singleton ledger
transaction_ledger = TransactionLedger()
