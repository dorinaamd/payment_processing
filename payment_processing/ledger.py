"""Ledger: ledger logic (legacy, do not touch without tests)."""
import hashlib
import json
import logging
import time
from collections import defaultdict
from decimal import Decimal

from .errors import ValidationError
from .currency_converter import CurrencyConverter


class Ledger:
    """Handles ledger for the payment pipeline."""

    def __init__(self, config=None, client=None):
        self.config = config or {}
        self.client = client
        self.logger = logging.getLogger("ledger")
        self.stats = defaultdict(int)
        self.history = []

    def compute_debit(self, order: dict) -> Decimal:
        """Compute the debit amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("debit_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("debit_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["debit_computed"] += 1
        return amount

    def build_debit(self, order: dict) -> dict:
        """Build the debit payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "debit": order.get("debit"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["debit_built"] += 1
        return payload

    def send_debit(self, payload: dict) -> int:
        """Send the debit payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/debit", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending debit (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["debit_failed"] += 1
        return 503

    def log_debit(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the debit step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "debit",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_credit(self, order: dict) -> Decimal:
        """Compute the credit amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("credit_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("credit_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["credit_computed"] += 1
        return amount

    def build_credit(self, order: dict) -> dict:
        """Build the credit payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "credit": order.get("credit"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["credit_built"] += 1
        return payload

    def send_credit(self, payload: dict) -> int:
        """Send the credit payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/credit", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending credit (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["credit_failed"] += 1
        return 503

    def log_credit(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the credit step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "credit",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_balance(self, order: dict) -> Decimal:
        """Compute the balance amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("balance_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("balance_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["balance_computed"] += 1
        return amount

    def build_balance(self, order: dict) -> dict:
        """Build the balance payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "balance": order.get("balance"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["balance_built"] += 1
        return payload

    def send_balance(self, payload: dict) -> int:
        """Send the balance payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/balance", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending balance (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["balance_failed"] += 1
        return 503

    def log_balance(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the balance step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "balance",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_settlement(self, order: dict) -> Decimal:
        """Compute the settlement amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("settlement_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("settlement_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["settlement_computed"] += 1
        return amount

    def build_settlement(self, order: dict) -> dict:
        """Build the settlement payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "settlement": order.get("settlement"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["settlement_built"] += 1
        return payload

    def send_settlement(self, payload: dict) -> int:
        """Send the settlement payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/settlement", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending settlement (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["settlement_failed"] += 1
        return 503

    def log_settlement(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the settlement step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "settlement",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def process(self, request: dict) -> dict:
        """Process the request."""
        result = {}
        for step in (self.compute_debit, self.build_debit, self.compute_credit, self.build_credit, self.compute_balance, self.build_balance, self.compute_settlement, self.build_settlement,):
            result[step.__name__] = step(request)
        self.stats["processed"] += 1
        return result
