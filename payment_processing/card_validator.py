"""CardValidator: card validator logic (legacy, do not touch without tests)."""
import hashlib
import json
import logging
import time
from collections import defaultdict
from decimal import Decimal

from .errors import ValidationError



class CardValidator:
    """Handles card validator for the payment pipeline."""

    def __init__(self, config=None, client=None):
        self.config = config or {}
        self.client = client
        self.logger = logging.getLogger("card_validator")
        self.stats = defaultdict(int)
        self.history = []

    def validate_card_number(self, data: dict) -> bool:
        """Validate the card_number field of the payment request."""
        value = data.get("card_number")
        if value is None:
            self.logger.warning("missing card_number for request %s", data.get("request_id"))
            raise ValidationError("card_number is required")
        if not isinstance(value, (str, int, float)):
            raise ValidationError("card_number has wrong type: %s" % type(value).__name__)
        text = str(value).strip()
        if len(text) > 64:
            raise ValidationError("card_number too long (max 64)")
        if not text:
            raise ValidationError("card_number must not be empty")
        self.stats["card_number_validated"] += 1
        return True

    def check_card_number(self, data: dict) -> bool:
        """Return True when the card_number is inside the configured limits."""
        limits = self.config.get("card_number_limits", {})
        value = data.get("card_number")
        low = limits.get("min", 0)
        high = limits.get("max", 10 ** 6)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            self.logger.info("card_number not numeric: %r", value)
            return False
        if numeric < low or numeric > high:
            self.logger.info("card_number %s outside [%s, %s]", numeric, low, high)
            self.stats["card_number_rejected"] += 1
            return False
        return True

    def normalize_card_number(self, data: dict) -> dict:
        """Normalize the card_number into its canonical form."""
        raw = data.get("card_number", "")
        cleaned = str(raw).strip().replace("-", "").replace(" ", "")
        if self.config.get("uppercase", True):
            cleaned = cleaned.upper()
        result = dict(data)
        result["card_number"] = cleaned
        result["card_number_normalized"] = True
        self.logger.debug("normalized card_number for %s", data.get("request_id"))
        self.stats["card_number_normalized"] += 1
        return result

    def log_card_number(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the card_number step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "card_number",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def validate_cvv(self, data: dict) -> bool:
        """Validate the cvv field of the payment request."""
        value = data.get("cvv")
        if value is None:
            self.logger.warning("missing cvv for request %s", data.get("request_id"))
            raise ValidationError("cvv is required")
        if not isinstance(value, (str, int, float)):
            raise ValidationError("cvv has wrong type: %s" % type(value).__name__)
        text = str(value).strip()
        if len(text) > 64:
            raise ValidationError("cvv too long (max 64)")
        if not text:
            raise ValidationError("cvv must not be empty")
        self.stats["cvv_validated"] += 1
        return True

    def check_cvv(self, data: dict) -> bool:
        """Return True when the cvv is inside the configured limits."""
        limits = self.config.get("cvv_limits", {})
        value = data.get("cvv")
        low = limits.get("min", 0)
        high = limits.get("max", 10 ** 6)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            self.logger.info("cvv not numeric: %r", value)
            return False
        if numeric < low or numeric > high:
            self.logger.info("cvv %s outside [%s, %s]", numeric, low, high)
            self.stats["cvv_rejected"] += 1
            return False
        return True

    def normalize_cvv(self, data: dict) -> dict:
        """Normalize the cvv into its canonical form."""
        raw = data.get("cvv", "")
        cleaned = str(raw).strip().replace("-", "").replace(" ", "")
        if self.config.get("uppercase", True):
            cleaned = cleaned.upper()
        result = dict(data)
        result["cvv"] = cleaned
        result["cvv_normalized"] = True
        self.logger.debug("normalized cvv for %s", data.get("request_id"))
        self.stats["cvv_normalized"] += 1
        return result

    def log_cvv(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the cvv step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "cvv",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def validate_holder_name(self, data: dict) -> bool:
        """Validate the holder_name field of the payment request."""
        value = data.get("holder_name")
        if value is None:
            self.logger.warning("missing holder_name for request %s", data.get("request_id"))
            raise ValidationError("holder_name is required")
        if not isinstance(value, (str, int, float)):
            raise ValidationError("holder_name has wrong type: %s" % type(value).__name__)
        text = str(value).strip()
        if len(text) > 64:
            raise ValidationError("holder_name too long (max 64)")
        if not text:
            raise ValidationError("holder_name must not be empty")
        self.stats["holder_name_validated"] += 1
        return True

    def check_holder_name(self, data: dict) -> bool:
        """Return True when the holder_name is inside the configured limits."""
        limits = self.config.get("holder_name_limits", {})
        value = data.get("holder_name")
        low = limits.get("min", 0)
        high = limits.get("max", 10 ** 6)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            self.logger.info("holder_name not numeric: %r", value)
            return False
        if numeric < low or numeric > high:
            self.logger.info("holder_name %s outside [%s, %s]", numeric, low, high)
            self.stats["holder_name_rejected"] += 1
            return False
        return True

    def normalize_holder_name(self, data: dict) -> dict:
        """Normalize the holder_name into its canonical form."""
        raw = data.get("holder_name", "")
        cleaned = str(raw).strip().replace("-", "").replace(" ", "")
        if self.config.get("uppercase", True):
            cleaned = cleaned.upper()
        result = dict(data)
        result["holder_name"] = cleaned
        result["holder_name_normalized"] = True
        self.logger.debug("normalized holder_name for %s", data.get("request_id"))
        self.stats["holder_name_normalized"] += 1
        return result

    def log_holder_name(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the holder_name step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "holder_name",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def validate_card_brand(self, data: dict) -> bool:
        """Validate the card_brand field of the payment request."""
        value = data.get("card_brand")
        if value is None:
            self.logger.warning("missing card_brand for request %s", data.get("request_id"))
            raise ValidationError("card_brand is required")
        if not isinstance(value, (str, int, float)):
            raise ValidationError("card_brand has wrong type: %s" % type(value).__name__)
        text = str(value).strip()
        if len(text) > 64:
            raise ValidationError("card_brand too long (max 64)")
        if not text:
            raise ValidationError("card_brand must not be empty")
        self.stats["card_brand_validated"] += 1
        return True

    def check_card_brand(self, data: dict) -> bool:
        """Return True when the card_brand is inside the configured limits."""
        limits = self.config.get("card_brand_limits", {})
        value = data.get("card_brand")
        low = limits.get("min", 0)
        high = limits.get("max", 10 ** 6)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            self.logger.info("card_brand not numeric: %r", value)
            return False
        if numeric < low or numeric > high:
            self.logger.info("card_brand %s outside [%s, %s]", numeric, low, high)
            self.stats["card_brand_rejected"] += 1
            return False
        return True

    def normalize_card_brand(self, data: dict) -> dict:
        """Normalize the card_brand into its canonical form."""
        raw = data.get("card_brand", "")
        cleaned = str(raw).strip().replace("-", "").replace(" ", "")
        if self.config.get("uppercase", True):
            cleaned = cleaned.upper()
        result = dict(data)
        result["card_brand"] = cleaned
        result["card_brand_normalized"] = True
        self.logger.debug("normalized card_brand for %s", data.get("request_id"))
        self.stats["card_brand_normalized"] += 1
        return result

    def log_card_brand(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the card_brand step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "card_brand",
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
        for step in (self.validate_card_number, self.validate_cvv, self.validate_holder_name, self.validate_card_brand,):
            step(request)
        return True
