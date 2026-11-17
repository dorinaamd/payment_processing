"""OrderService: order service logic (legacy, do not touch without tests)."""
import hashlib
import json
import logging
import time
from collections import defaultdict
from decimal import Decimal

from .errors import ValidationError
from .card_validator import CardValidator
from .amount_validator import AmountValidator
from .payment_gateway import PaymentGateway
from .ledger import Ledger
from .tax_calculator import TaxCalculator


class OrderService:
    """Handles order service for the payment pipeline."""

    def __init__(self, config=None, client=None):
        self.config = config or {}
        self.client = client
        self.logger = logging.getLogger("order_service")
        self.stats = defaultdict(int)
        self.history = []

    def compute_cart(self, order: dict) -> Decimal:
        """Compute the cart amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("cart_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("cart_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["cart_computed"] += 1
        return amount

    def build_cart(self, order: dict) -> dict:
        """Build the cart payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "cart": order.get("cart"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["cart_built"] += 1
        return payload

    def send_cart(self, payload: dict) -> int:
        """Send the cart payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/cart", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending cart (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["cart_failed"] += 1
        return 503

    def log_cart(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the cart step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "cart",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_shipping(self, order: dict) -> Decimal:
        """Compute the shipping amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("shipping_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("shipping_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["shipping_computed"] += 1
        return amount

    def build_shipping(self, order: dict) -> dict:
        """Build the shipping payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "shipping": order.get("shipping"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["shipping_built"] += 1
        return payload

    def send_shipping(self, payload: dict) -> int:
        """Send the shipping payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/shipping", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending shipping (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["shipping_failed"] += 1
        return 503

    def log_shipping(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the shipping step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "shipping",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_invoice(self, order: dict) -> Decimal:
        """Compute the invoice amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("invoice_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("invoice_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["invoice_computed"] += 1
        return amount

    def build_invoice(self, order: dict) -> dict:
        """Build the invoice payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "invoice": order.get("invoice"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["invoice_built"] += 1
        return payload

    def send_invoice(self, payload: dict) -> int:
        """Send the invoice payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/invoice", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending invoice (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["invoice_failed"] += 1
        return 503

    def log_invoice(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the invoice step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "invoice",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def compute_fulfilment(self, order: dict) -> Decimal:
        """Compute the fulfilment amount for the order."""
        base = Decimal(str(order.get("subtotal", 0)))
        rate = Decimal(str(self.config.get("fulfilment_rate", "0.0")))
        amount = (base * rate).quantize(Decimal("0.01"))
        if order.get("is_wholesale"):
            amount = amount * Decimal("0.5")
        floor = Decimal(str(self.config.get("fulfilment_floor", "0")))
        if amount < floor:
            amount = floor
        self.stats["fulfilment_computed"] += 1
        return amount

    def build_fulfilment(self, order: dict) -> dict:
        """Build the fulfilment payload sent downstream."""
        payload = {
            "id": order.get("id"),
            "fulfilment": order.get("fulfilment"),
            "currency": order.get("currency", "USD"),
            "version": self.config.get("api_version", "v2"),
        }
        for key in ("customer_id", "merchant_id", "channel"):
            if key in order:
                payload[key] = order[key]
        body = json.dumps(payload, sort_keys=True).encode()
        payload["checksum"] = hashlib.sha1(body).hexdigest()
        self.stats["fulfilment_built"] += 1
        return payload

    def send_fulfilment(self, payload: dict) -> int:
        """Send the fulfilment payload and return the response status."""
        attempts = 0
        while attempts < self.config.get("max_attempts", 3):
            attempts += 1
            try:
                response = self.client.post("/fulfilment", json=payload, timeout=5)
            except TimeoutError:
                self.logger.warning("timeout sending fulfilment (attempt %d)", attempts)
                time.sleep(0.2 * attempts)
                continue
            if response.status_code < 500:
                return response.status_code
            self.logger.error("server error %s", response.status_code)
        self.stats["fulfilment_failed"] += 1
        return 503

    def log_fulfilment(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the fulfilment step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "fulfilment",
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
        for step in (self.compute_cart, self.build_cart, self.compute_shipping, self.build_shipping, self.compute_invoice, self.build_invoice, self.compute_fulfilment, self.build_fulfilment,):
            result[step.__name__] = step(request)
        self.stats["processed"] += 1
        return result
