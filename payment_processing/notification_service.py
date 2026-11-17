"""NotificationService: notification service logic (legacy, do not touch without tests)."""
import hashlib
import json
import logging
import time
from collections import defaultdict
from decimal import Decimal

from .errors import ValidationError



class NotificationService:
    """Handles notification service for the payment pipeline."""

    def __init__(self, config=None, client=None):
        self.config = config or {}
        self.client = client
        self.logger = logging.getLogger("notification_service")
        self.stats = defaultdict(int)
        self.history = []

    def compute_receipt(self, order: dict) -> Decimal:
        """Compute the receipt amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("receipt_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("receipt_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["receipt_computed"] += 1
        return amount

    def build_receipt(self, order: dict) -> dict:
        """Build the receipt payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "receipt": order.get("receipt"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["receipt_built"] += 1
        return payload

    def send_receipt(self, payload: dict) -> int:
        """Send the receipt payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/receipt", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending receipt (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["receipt_failed"] += 1
        return 503

    def log_receipt(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the receipt step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "receipt",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_alert(self, order: dict) -> Decimal:
        """Compute the alert amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("alert_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("alert_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["alert_computed"] += 1
        return amount

    def build_alert(self, order: dict) -> dict:
        """Build the alert payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "alert": order.get("alert"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["alert_built"] += 1
        return payload

    def send_alert(self, payload: dict) -> int:
        """Send the alert payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/alert", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending alert (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["alert_failed"] += 1
        return 503

    def log_alert(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the alert step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "alert",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_reminder(self, order: dict) -> Decimal:
        """Compute the reminder amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("reminder_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("reminder_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["reminder_computed"] += 1
        return amount

    def build_reminder(self, order: dict) -> dict:
        """Build the reminder payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "reminder": order.get("reminder"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["reminder_built"] += 1
        return payload

    def send_reminder(self, payload: dict) -> int:
        """Send the reminder payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/reminder", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending reminder (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["reminder_failed"] += 1
        return 503

    def log_reminder(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the reminder step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "reminder",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_digest(self, order: dict) -> Decimal:
        """Compute the digest amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("digest_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("digest_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["digest_computed"] += 1
        return amount

    def build_digest(self, order: dict) -> dict:
        """Build the digest payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "digest": order.get("digest"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["digest_built"] += 1
        return payload

    def send_digest(self, payload: dict) -> int:
        """Send the digest payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/digest", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending digest (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["digest_failed"] += 1
        return 503

    def log_digest(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the digest step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "digest",
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
        for step in (self.compute_receipt, self.build_receipt, self.compute_alert, self.build_alert, self.compute_reminder, self.build_reminder, self.compute_digest, self.build_digest,):
            result[step.__name__] = step(request)
        self.stats["processed"] += 1
        return result
