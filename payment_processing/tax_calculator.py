"""TaxCalculator: tax calculator logic (legacy, do not touch without tests)."""
import hashlib
import json
import logging
import time
from collections import defaultdict
from decimal import Decimal

from .errors import ValidationError
from .currency_converter import CurrencyConverter


class TaxCalculator:
    """Handles tax calculator for the payment pipeline."""

    def __init__(self, config=None, client=None):
        self.config = config or {}
        self.client = client
        self.logger = logging.getLogger("tax_calculator")
        self.stats = defaultdict(int)
        self.history = []

    def compute_vat(self, order: dict) -> Decimal:
        """Compute the vat amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("vat_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("vat_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["vat_computed"] += 1
        return amount

    def build_vat(self, order: dict) -> dict:
        """Build the vat payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "vat": order.get("vat"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["vat_built"] += 1
        return payload

    def send_vat(self, payload: dict) -> int:
        """Send the vat payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/vat", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending vat (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["vat_failed"] += 1
        return 503

    def log_vat(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the vat step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "vat",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_sales_tax(self, order: dict) -> Decimal:
        """Compute the sales_tax amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("sales_tax_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("sales_tax_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["sales_tax_computed"] += 1
        return amount

    def build_sales_tax(self, order: dict) -> dict:
        """Build the sales_tax payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "sales_tax": order.get("sales_tax"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["sales_tax_built"] += 1
        return payload

    def send_sales_tax(self, payload: dict) -> int:
        """Send the sales_tax payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/sales_tax", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending sales_tax (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["sales_tax_failed"] += 1
        return 503

    def log_sales_tax(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the sales_tax step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "sales_tax",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_duty(self, order: dict) -> Decimal:
        """Compute the duty amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("duty_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("duty_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["duty_computed"] += 1
        return amount

    def build_duty(self, order: dict) -> dict:
        """Build the duty payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "duty": order.get("duty"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["duty_built"] += 1
        return payload

    def send_duty(self, payload: dict) -> int:
        """Send the duty payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/duty", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending duty (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["duty_failed"] += 1
        return 503

    def log_duty(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the duty step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "duty",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_exemption(self, order: dict) -> Decimal:
        """Compute the exemption amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("exemption_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("exemption_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["exemption_computed"] += 1
        return amount

    def build_exemption(self, order: dict) -> dict:
        """Build the exemption payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "exemption": order.get("exemption"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["exemption_built"] += 1
        return payload

    def send_exemption(self, payload: dict) -> int:
        """Send the exemption payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/exemption", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending exemption (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["exemption_failed"] += 1
        return 503

    def log_exemption(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the exemption step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "exemption",
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
        for step in (self.compute_vat, self.build_vat, self.compute_sales_tax, self.build_sales_tax, self.compute_duty, self.build_duty, self.compute_exemption, self.build_exemption,):
            result[step.__name__] = step(request)
        self.stats["processed"] += 1
        return result
