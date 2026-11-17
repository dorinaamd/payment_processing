"""CurrencyConverter: currency converter logic (legacy, do not touch without tests)."""
import hashlib
import json
import logging
import time
from collections import defaultdict
from decimal import Decimal

from .errors import ValidationError



class CurrencyConverter:
    """Handles currency converter for the payment pipeline."""

    def __init__(self, config=None, client=None):
        self.config = config or {}
        self.client = client
        self.logger = logging.getLogger("currency_converter")
        self.stats = defaultdict(int)
        self.history = []

    def compute_rate(self, order: dict) -> Decimal:
        """Compute the rate amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("rate_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("rate_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["rate_computed"] += 1
        return amount

    def build_rate(self, order: dict) -> dict:
        """Build the rate payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "rate": order.get("rate"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["rate_built"] += 1
        return payload

    def send_rate(self, payload: dict) -> int:
        """Send the rate payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/rate", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending rate (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["rate_failed"] += 1
        return 503

    def log_rate(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the rate step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "rate",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_spread(self, order: dict) -> Decimal:
        """Compute the spread amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("spread_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("spread_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["spread_computed"] += 1
        return amount

    def build_spread(self, order: dict) -> dict:
        """Build the spread payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "spread": order.get("spread"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["spread_built"] += 1
        return payload

    def send_spread(self, payload: dict) -> int:
        """Send the spread payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/spread", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending spread (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["spread_failed"] += 1
        return 503

    def log_spread(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the spread step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "spread",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_rounding(self, order: dict) -> Decimal:
        """Compute the rounding amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("rounding_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("rounding_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["rounding_computed"] += 1
        return amount

    def build_rounding(self, order: dict) -> dict:
        """Build the rounding payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "rounding": order.get("rounding"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["rounding_built"] += 1
        return payload

    def send_rounding(self, payload: dict) -> int:
        """Send the rounding payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/rounding", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending rounding (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["rounding_failed"] += 1
        return 503

    def log_rounding(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the rounding step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "rounding",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_fee(self, order: dict) -> Decimal:
        """Compute the fee amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("fee_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("fee_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["fee_computed"] += 1
        return amount

    def build_fee(self, order: dict) -> dict:
        """Build the fee payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "fee": order.get("fee"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["fee_built"] += 1
        return payload

    def send_fee(self, payload: dict) -> int:
        """Send the fee payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/fee", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending fee (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["fee_failed"] += 1
        return 503

    def log_fee(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the fee step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "fee",
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
        for step in (self.compute_rate, self.build_rate, self.compute_spread, self.build_spread, self.compute_rounding, self.build_rounding, self.compute_fee, self.build_fee,):
            result[step.__name__] = step(request)
        self.stats["processed"] += 1
        return result
