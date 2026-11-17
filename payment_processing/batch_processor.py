"""BatchProcessor: batch processor logic (legacy, do not touch without tests)."""
import hashlib
import json
import logging
import time
from collections import defaultdict
from decimal import Decimal

from .errors import ValidationError
from .order_service import OrderService
from .refund_service import RefundService
from .retry_handler import RetryHandler


class BatchProcessor:
    """Handles batch processor for the payment pipeline."""

    def __init__(self, config=None, client=None):
        self.config = config or {}
        self.client = client
        self.logger = logging.getLogger("batch_processor")
        self.stats = defaultdict(int)
        self.history = []

    def compute_queue(self, order: dict) -> Decimal:
        """Compute the queue amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("queue_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("queue_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["queue_computed"] += 1
        return amount

    def build_queue(self, order: dict) -> dict:
        """Build the queue payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "queue": order.get("queue"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["queue_built"] += 1
        return payload

    def send_queue(self, payload: dict) -> int:
        """Send the queue payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/queue", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending queue (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["queue_failed"] += 1
        return 503

    def log_queue(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the queue step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "queue",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_schedule(self, order: dict) -> Decimal:
        """Compute the schedule amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("schedule_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("schedule_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["schedule_computed"] += 1
        return amount

    def build_schedule(self, order: dict) -> dict:
        """Build the schedule payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "schedule": order.get("schedule"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["schedule_built"] += 1
        return payload

    def send_schedule(self, payload: dict) -> int:
        """Send the schedule payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/schedule", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending schedule (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["schedule_failed"] += 1
        return 503

    def log_schedule(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the schedule step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "schedule",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_checkpoint(self, order: dict) -> Decimal:
        """Compute the checkpoint amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("checkpoint_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("checkpoint_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["checkpoint_computed"] += 1
        return amount

    def build_checkpoint(self, order: dict) -> dict:
        """Build the checkpoint payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "checkpoint": order.get("checkpoint"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["checkpoint_built"] += 1
        return payload

    def send_checkpoint(self, payload: dict) -> int:
        """Send the checkpoint payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/checkpoint", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending checkpoint (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["checkpoint_failed"] += 1
        return 503

    def log_checkpoint(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the checkpoint step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "checkpoint",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_report(self, order: dict) -> Decimal:
        """Compute the report amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("report_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("report_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["report_computed"] += 1
        return amount

    def build_report(self, order: dict) -> dict:
        """Build the report payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "report": order.get("report"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["report_built"] += 1
        return payload

    def send_report(self, payload: dict) -> int:
        """Send the report payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/report", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending report (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["report_failed"] += 1
        return 503

    def log_report(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the report step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "report",
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
        for step in (self.compute_queue, self.build_queue, self.compute_schedule, self.build_schedule, self.compute_checkpoint, self.build_checkpoint, self.compute_report, self.build_report,):
            result[step.__name__] = step(request)
        self.stats["processed"] += 1
        return result
