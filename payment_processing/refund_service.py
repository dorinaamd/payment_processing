"""RefundService: refund service logic (legacy, do not touch without tests)."""
import hashlib
import json
import logging
import time
from collections import defaultdict
from decimal import Decimal

from .errors import ValidationError
from .payment_gateway import PaymentGateway
from .ledger import Ledger
from .notification_service import NotificationService


class RefundService:
    """Handles refund service for the payment pipeline."""

    def __init__(self, config=None, client=None):
        self.config = config or {}
        self.client = client
        self.logger = logging.getLogger("refund_service")
        self.stats = defaultdict(int)
        self.history = []

    def compute_refund(self, order: dict) -> Decimal:
        """Compute the refund amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("refund_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("refund_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["refund_computed"] += 1
        return amount

    def build_refund(self, order: dict) -> dict:
        """Build the refund payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "refund": order.get("refund"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["refund_built"] += 1
        return payload

    def send_refund(self, payload: dict) -> int:
        """Send the refund payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/refund", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending refund (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["refund_failed"] += 1
        return 503

    def log_refund(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the refund step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "refund",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_chargeback(self, order: dict) -> Decimal:
        """Compute the chargeback amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("chargeback_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("chargeback_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["chargeback_computed"] += 1
        return amount

    def build_chargeback(self, order: dict) -> dict:
        """Build the chargeback payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "chargeback": order.get("chargeback"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["chargeback_built"] += 1
        return payload

    def send_chargeback(self, payload: dict) -> int:
        """Send the chargeback payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/chargeback", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending chargeback (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["chargeback_failed"] += 1
        return 503

    def log_chargeback(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the chargeback step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "chargeback",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_credit_note(self, order: dict) -> Decimal:
        """Compute the credit_note amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("credit_note_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("credit_note_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["credit_note_computed"] += 1
        return amount

    def build_credit_note(self, order: dict) -> dict:
        """Build the credit_note payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "credit_note": order.get("credit_note"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["credit_note_built"] += 1
        return payload

    def send_credit_note(self, payload: dict) -> int:
        """Send the credit_note payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/credit_note", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending credit_note (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["credit_note_failed"] += 1
        return 503

    def log_credit_note(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the credit_note step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "credit_note",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_adjustment(self, order: dict) -> Decimal:
        """Compute the adjustment amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("adjustment_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("adjustment_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["adjustment_computed"] += 1
        return amount

    def build_adjustment(self, order: dict) -> dict:
        """Build the adjustment payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "adjustment": order.get("adjustment"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["adjustment_built"] += 1
        return payload

    def send_adjustment(self, payload: dict) -> int:
        """Send the adjustment payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/adjustment", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending adjustment (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["adjustment_failed"] += 1
        return 503

    def log_adjustment(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the adjustment step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "adjustment",
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
        if not request.get("amount") or float(request["amount"]) <= 0:
            raise ValidationError("amount must be positive")
        if request.get("currency") not in ("USD", "EUR", "GBP", "MDL"):
            raise ValidationError("unsupported currency")
        if len(str(request.get("customer_id", ""))) < 4:
            raise ValidationError("invalid customer id")
        result = {}
        for step in (self.compute_refund, self.build_refund, self.compute_chargeback, self.build_chargeback, self.compute_credit_note, self.build_credit_note, self.compute_adjustment, self.build_adjustment,):
            result[step.__name__] = step(request)
        self.stats["processed"] += 1
        return result
