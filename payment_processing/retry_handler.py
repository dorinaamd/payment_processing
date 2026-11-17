"""RetryHandler: retry handler logic (legacy, do not touch without tests)."""
import hashlib
import json
import logging
import time
from collections import defaultdict
from decimal import Decimal

from .errors import ValidationError



class RetryHandler:
    """Handles retry handler for the payment pipeline."""

    def __init__(self, config=None, client=None):
        self.config = config or {}
        self.client = client
        self.logger = logging.getLogger("retry_handler")
        self.stats = defaultdict(int)
        self.history = []

    def compute_backoff(self, order: dict) -> Decimal:
        """Compute the backoff amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("backoff_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("backoff_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["backoff_computed"] += 1
        return amount

    def build_backoff(self, order: dict) -> dict:
        """Build the backoff payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "backoff": order.get("backoff"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["backoff_built"] += 1
        return payload

    def send_backoff(self, payload: dict) -> int:
        """Send the backoff payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/backoff", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending backoff (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["backoff_failed"] += 1
        return 503

    def log_backoff(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the backoff step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "backoff",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_deadline(self, order: dict) -> Decimal:
        """Compute the deadline amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("deadline_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("deadline_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["deadline_computed"] += 1
        return amount

    def build_deadline(self, order: dict) -> dict:
        """Build the deadline payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "deadline": order.get("deadline"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["deadline_built"] += 1
        return payload

    def send_deadline(self, payload: dict) -> int:
        """Send the deadline payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/deadline", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending deadline (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["deadline_failed"] += 1
        return 503

    def log_deadline(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the deadline step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "deadline",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_dead_letter(self, order: dict) -> Decimal:
        """Compute the dead_letter amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("dead_letter_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("dead_letter_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["dead_letter_computed"] += 1
        return amount

    def build_dead_letter(self, order: dict) -> dict:
        """Build the dead_letter payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "dead_letter": order.get("dead_letter"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["dead_letter_built"] += 1
        return payload

    def send_dead_letter(self, payload: dict) -> int:
        """Send the dead_letter payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/dead_letter", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending dead_letter (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["dead_letter_failed"] += 1
        return 503

    def log_dead_letter(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the dead_letter step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "dead_letter",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_jitter(self, order: dict) -> Decimal:
        """Compute the jitter amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("jitter_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("jitter_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["jitter_computed"] += 1
        return amount

    def build_jitter(self, order: dict) -> dict:
        """Build the jitter payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "jitter": order.get("jitter"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["jitter_built"] += 1
        return payload

    def send_jitter(self, payload: dict) -> int:
        """Send the jitter payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/jitter", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending jitter (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["jitter_failed"] += 1
        return 503

    def log_jitter(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the jitter step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "jitter",
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
        for step in (self.compute_backoff, self.build_backoff, self.compute_deadline, self.build_deadline, self.compute_dead_letter, self.build_dead_letter, self.compute_jitter, self.build_jitter,):
            result[step.__name__] = step(request)
        self.stats["processed"] += 1
        return result
