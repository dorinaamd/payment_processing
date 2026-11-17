"""AmountValidator: amount validator logic (legacy, do not touch without tests)."""
import hashlib
import json
import logging
import time
from collections import defaultdict
from decimal import Decimal

from .errors import ValidationError



class AmountValidator:
    """Handles amount validator for the payment pipeline."""

    def __init__(self, config=None, client=None):
        self.config = config or {}
        self.client = client
        self.logger = logging.getLogger("amount_validator")
        self.stats = defaultdict(int)
        self.history = []

    def validate_amount(self, data: dict) -> bool:
        """Validate the amount field of the payment request."""
        value = data.get("amount")
        if value is None:
            self.logger.warning("missing amount for request %s", data.get("request_id"))
            raise ValidationError("amount is required")
        if not isinstance(value, (str, int, float)):
            raise ValidationError("amount has wrong type: %s" % type(value).__name__)
        text = str(value).strip()
        if len(text) > 64:
            raise ValidationError("amount too long (max 64)")
        if not text:
            raise ValidationError("amount must not be empty")
        self.stats["amount_validated"] += 1
        return True

    def check_amount(self, data: dict) -> bool:
        """Return True when the amount is inside the configured limits."""
        limits = self.config.get("amount_limits", {})
        value = data.get("amount")
        low = limits.get("min", 0)
        high = limits.get("max", 10 ** 6)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            self.logger.info("amount not numeric: %r", value)
            return False
        if numeric < low or numeric > high:
            self.logger.info("amount %s outside [%s, %s]", numeric, low, high)
            self.stats["amount_rejected"] += 1
            return False
        return True

    def normalize_amount(self, data: dict) -> dict:
        """Normalize the amount into its canonical form."""
        raw = data.get("amount", "")
        cleaned = str(raw).strip().replace("-", "").replace(" ", "")
        if self.config.get("uppercase", True):
            cleaned = cleaned.upper()
        result = dict(data)
        result["amount"] = cleaned
        result["amount_normalized"] = True
        self.logger.debug("normalized amount for %s", data.get("request_id"))
        self.stats["amount_normalized"] += 1
        return result

    def log_amount(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the amount step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "amount",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def validate_limit(self, data: dict) -> bool:
        """Validate the limit field of the payment request."""
        value = data.get("limit")
        if value is None:
            self.logger.warning("missing limit for request %s", data.get("request_id"))
            raise ValidationError("limit is required")
        if not isinstance(value, (str, int, float)):
            raise ValidationError("limit has wrong type: %s" % type(value).__name__)
        text = str(value).strip()
        if len(text) > 64:
            raise ValidationError("limit too long (max 64)")
        if not text:
            raise ValidationError("limit must not be empty")
        self.stats["limit_validated"] += 1
        return True

    def check_limit(self, data: dict) -> bool:
        """Return True when the limit is inside the configured limits."""
        limits = self.config.get("limit_limits", {})
        value = data.get("limit")
        low = limits.get("min", 0)
        high = limits.get("max", 10 ** 6)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            self.logger.info("limit not numeric: %r", value)
            return False
        if numeric < low or numeric > high:
            self.logger.info("limit %s outside [%s, %s]", numeric, low, high)
            self.stats["limit_rejected"] += 1
            return False
        return True

    def normalize_limit(self, data: dict) -> dict:
        """Normalize the limit into its canonical form."""
        raw = data.get("limit", "")
        cleaned = str(raw).strip().replace("-", "").replace(" ", "")
        if self.config.get("uppercase", True):
            cleaned = cleaned.upper()
        result = dict(data)
        result["limit"] = cleaned
        result["limit_normalized"] = True
        self.logger.debug("normalized limit for %s", data.get("request_id"))
        self.stats["limit_normalized"] += 1
        return result

    def log_limit(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the limit step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "limit",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def validate_installments(self, data: dict) -> bool:
        """Validate the installments field of the payment request."""
        value = data.get("installments")
        if value is None:
            self.logger.warning("missing installments for request %s", data.get("request_id"))
            raise ValidationError("installments is required")
        if not isinstance(value, (str, int, float)):
            raise ValidationError("installments has wrong type: %s" % type(value).__name__)
        text = str(value).strip()
        if len(text) > 64:
            raise ValidationError("installments too long (max 64)")
        if not text:
            raise ValidationError("installments must not be empty")
        self.stats["installments_validated"] += 1
        return True

    def check_installments(self, data: dict) -> bool:
        """Return True when the installments is inside the configured limits."""
        limits = self.config.get("installments_limits", {})
        value = data.get("installments")
        low = limits.get("min", 0)
        high = limits.get("max", 10 ** 6)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            self.logger.info("installments not numeric: %r", value)
            return False
        if numeric < low or numeric > high:
            self.logger.info("installments %s outside [%s, %s]", numeric, low, high)
            self.stats["installments_rejected"] += 1
            return False
        return True

    def normalize_installments(self, data: dict) -> dict:
        """Normalize the installments into its canonical form."""
        raw = data.get("installments", "")
        cleaned = str(raw).strip().replace("-", "").replace(" ", "")
        if self.config.get("uppercase", True):
            cleaned = cleaned.upper()
        result = dict(data)
        result["installments"] = cleaned
        result["installments_normalized"] = True
        self.logger.debug("normalized installments for %s", data.get("request_id"))
        self.stats["installments_normalized"] += 1
        return result

    def log_installments(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the installments step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "installments",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def validate_discount(self, data: dict) -> bool:
        """Validate the discount field of the payment request."""
        value = data.get("discount")
        if value is None:
            self.logger.warning("missing discount for request %s", data.get("request_id"))
            raise ValidationError("discount is required")
        if not isinstance(value, (str, int, float)):
            raise ValidationError("discount has wrong type: %s" % type(value).__name__)
        text = str(value).strip()
        if len(text) > 64:
            raise ValidationError("discount too long (max 64)")
        if not text:
            raise ValidationError("discount must not be empty")
        self.stats["discount_validated"] += 1
        return True

    def check_discount(self, data: dict) -> bool:
        """Return True when the discount is inside the configured limits."""
        limits = self.config.get("discount_limits", {})
        value = data.get("discount")
        low = limits.get("min", 0)
        high = limits.get("max", 10 ** 6)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            self.logger.info("discount not numeric: %r", value)
            return False
        if numeric < low or numeric > high:
            self.logger.info("discount %s outside [%s, %s]", numeric, low, high)
            self.stats["discount_rejected"] += 1
            return False
        return True

    def normalize_discount(self, data: dict) -> dict:
        """Normalize the discount into its canonical form."""
        raw = data.get("discount", "")
        cleaned = str(raw).strip().replace("-", "").replace(" ", "")
        if self.config.get("uppercase", True):
            cleaned = cleaned.upper()
        result = dict(data)
        result["discount"] = cleaned
        result["discount_normalized"] = True
        self.logger.debug("normalized discount for %s", data.get("request_id"))
        self.stats["discount_normalized"] += 1
        return result

    def log_discount(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the discount step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "discount",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def process(self, request: dict) -> bool:
        """Run every step for this request."""
        for step in (self.validate_amount, self.validate_limit, self.validate_installments, self.validate_discount,):
            step(request)
        return True
