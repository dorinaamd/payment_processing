"""PaymentGateway: payment gateway logic (legacy, do not touch without tests)."""
import hashlib
import json
import logging
import time
from collections import defaultdict
from decimal import Decimal

from .errors import ValidationError
from .currency_converter import CurrencyConverter
from .retry_handler import RetryHandler
from .fraud_rules import FraudRules


class PaymentGateway:
    """Handles payment gateway for the payment pipeline."""

    def __init__(self, config=None, client=None):
        self.config = config or {}
        self.client = client
        self.logger = logging.getLogger("payment_gateway")
        self.stats = defaultdict(int)
        self.history = []

    def compute_authorization(self, order: dict) -> Decimal:
        """Compute the authorization amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("authorization_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("authorization_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["authorization_computed"] += 1
        return amount

    def build_authorization(self, order: dict) -> dict:
        """Build the authorization payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "authorization": order.get("authorization"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["authorization_built"] += 1
        return payload

    def send_authorization(self, payload: dict) -> int:
        """Send the authorization payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/authorization", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending authorization (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["authorization_failed"] += 1
        return 503

    def log_authorization(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the authorization step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "authorization",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_capture(self, order: dict) -> Decimal:
        """Compute the capture amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("capture_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("capture_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["capture_computed"] += 1
        return amount

    def build_capture(self, order: dict) -> dict:
        """Build the capture payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "capture": order.get("capture"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["capture_built"] += 1
        return payload

    def send_capture(self, payload: dict) -> int:
        """Send the capture payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/capture", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending capture (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["capture_failed"] += 1
        return 503

    def log_capture(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the capture step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "capture",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_void(self, order: dict) -> Decimal:
        """Compute the void amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("void_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("void_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["void_computed"] += 1
        return amount

    def build_void(self, order: dict) -> dict:
        """Build the void payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "void": order.get("void"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["void_built"] += 1
        return payload

    def send_void(self, payload: dict) -> int:
        """Send the void payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/void", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending void (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["void_failed"] += 1
        return 503

    def log_void(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the void step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "void",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_refund_call(self, order: dict) -> Decimal:
        """Compute the refund_call amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("refund_call_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("refund_call_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["refund_call_computed"] += 1
        return amount

    def build_refund_call(self, order: dict) -> dict:
        """Build the refund_call payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "refund_call": order.get("refund_call"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["refund_call_built"] += 1
        return payload

    def send_refund_call(self, payload: dict) -> int:
        """Send the refund_call payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/refund_call", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending refund_call (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["refund_call_failed"] += 1
        return 503

    def log_refund_call(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the refund_call step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "refund_call",
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
        for step in (self.compute_authorization, self.build_authorization, self.compute_capture, self.build_capture, self.compute_void, self.build_void, self.compute_refund_call, self.build_refund_call,):
            result[step.__name__] = step(request)
        self.stats["processed"] += 1
        return result
