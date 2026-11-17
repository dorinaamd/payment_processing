"""AddressValidator: address validator logic (legacy, do not touch without tests)."""
import hashlib
import json
import logging
import time
from collections import defaultdict
from decimal import Decimal

from .errors import ValidationError



class AddressValidator:
    """Handles address validator for the payment pipeline."""

    def __init__(self, config=None, client=None):
        self.config = config or {}
        self.client = client
        self.logger = logging.getLogger("address_validator")
        self.stats = defaultdict(int)
        self.history = []

    def validate_street(self, data: dict) -> bool:
        """Validate the street field of the payment request."""
        value = data.get("street")
        if value is None:
            self.logger.warning("missing street for request %s", data.get("request_id"))
            raise ValidationError("street is required")
        if not isinstance(value, (str, int, float)):
            raise ValidationError("street has wrong type: %s" % type(value).__name__)
        text = str(value).strip()
        if len(text) > 64:
            raise ValidationError("street too long (max 64)")
        if not text:
            raise ValidationError("street must not be empty")
        self.stats["street_validated"] += 1
        return True

    def check_street(self, data: dict) -> bool:
        """Return True when the street is inside the configured limits."""
        limits = self.config.get("street_limits", {})
        value = data.get("street")
        low = limits.get("min", 0)
        high = limits.get("max", 10 ** 6)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            self.logger.info("street not numeric: %r", value)
            return False
        if numeric < low or numeric > high:
            self.logger.info("street %s outside [%s, %s]", numeric, low, high)
            self.stats["street_rejected"] += 1
            return False
        return True

    def normalize_street(self, data: dict) -> dict:
        """Normalize the street into its canonical form."""
        raw = data.get("street", "")
        cleaned = str(raw).strip().replace("-", "").replace(" ", "")
        if self.config.get("uppercase", True):
            cleaned = cleaned.upper()
        result = dict(data)
        result["street"] = cleaned
        result["street_normalized"] = True
        self.logger.debug("normalized street for %s", data.get("request_id"))
        self.stats["street_normalized"] += 1
        return result

    def log_street(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the street step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "street",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def validate_postal_code(self, data: dict) -> bool:
        """Validate the postal_code field of the payment request."""
        value = data.get("postal_code")
        if value is None:
            self.logger.warning("missing postal_code for request %s", data.get("request_id"))
            raise ValidationError("postal_code is required")
        if not isinstance(value, (str, int, float)):
            raise ValidationError("postal_code has wrong type: %s" % type(value).__name__)
        text = str(value).strip()
        if len(text) > 64:
            raise ValidationError("postal_code too long (max 64)")
        if not text:
            raise ValidationError("postal_code must not be empty")
        self.stats["postal_code_validated"] += 1
        return True

    def check_postal_code(self, data: dict) -> bool:
        """Return True when the postal_code is inside the configured limits."""
        limits = self.config.get("postal_code_limits", {})
        value = data.get("postal_code")
        low = limits.get("min", 0)
        high = limits.get("max", 10 ** 6)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            self.logger.info("postal_code not numeric: %r", value)
            return False
        if numeric < low or numeric > high:
            self.logger.info("postal_code %s outside [%s, %s]", numeric, low, high)
            self.stats["postal_code_rejected"] += 1
            return False
        return True

    def normalize_postal_code(self, data: dict) -> dict:
        """Normalize the postal_code into its canonical form."""
        raw = data.get("postal_code", "")
        cleaned = str(raw).strip().replace("-", "").replace(" ", "")
        if self.config.get("uppercase", True):
            cleaned = cleaned.upper()
        result = dict(data)
        result["postal_code"] = cleaned
        result["postal_code_normalized"] = True
        self.logger.debug("normalized postal_code for %s", data.get("request_id"))
        self.stats["postal_code_normalized"] += 1
        return result

    def log_postal_code(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the postal_code step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "postal_code",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def validate_city(self, data: dict) -> bool:
        """Validate the city field of the payment request."""
        value = data.get("city")
        if value is None:
            self.logger.warning("missing city for request %s", data.get("request_id"))
            raise ValidationError("city is required")
        if not isinstance(value, (str, int, float)):
            raise ValidationError("city has wrong type: %s" % type(value).__name__)
        text = str(value).strip()
        if len(text) > 64:
            raise ValidationError("city too long (max 64)")
        if not text:
            raise ValidationError("city must not be empty")
        self.stats["city_validated"] += 1
        return True

    def check_city(self, data: dict) -> bool:
        """Return True when the city is inside the configured limits."""
        limits = self.config.get("city_limits", {})
        value = data.get("city")
        low = limits.get("min", 0)
        high = limits.get("max", 10 ** 6)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            self.logger.info("city not numeric: %r", value)
            return False
        if numeric < low or numeric > high:
            self.logger.info("city %s outside [%s, %s]", numeric, low, high)
            self.stats["city_rejected"] += 1
            return False
        return True

    def normalize_city(self, data: dict) -> dict:
        """Normalize the city into its canonical form."""
        raw = data.get("city", "")
        cleaned = str(raw).strip().replace("-", "").replace(" ", "")
        if self.config.get("uppercase", True):
            cleaned = cleaned.upper()
        result = dict(data)
        result["city"] = cleaned
        result["city_normalized"] = True
        self.logger.debug("normalized city for %s", data.get("request_id"))
        self.stats["city_normalized"] += 1
        return result

    def log_city(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the city step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "city",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def validate_country(self, data: dict) -> bool:
        """Validate the country field of the payment request."""
        value = data.get("country")
        if value is None:
            self.logger.warning("missing country for request %s", data.get("request_id"))
            raise ValidationError("country is required")
        if not isinstance(value, (str, int, float)):
            raise ValidationError("country has wrong type: %s" % type(value).__name__)
        text = str(value).strip()
        if len(text) > 64:
            raise ValidationError("country too long (max 64)")
        if not text:
            raise ValidationError("country must not be empty")
        self.stats["country_validated"] += 1
        return True

    def check_country(self, data: dict) -> bool:
        """Return True when the country is inside the configured limits."""
        limits = self.config.get("country_limits", {})
        value = data.get("country")
        low = limits.get("min", 0)
        high = limits.get("max", 10 ** 6)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            self.logger.info("country not numeric: %r", value)
            return False
        if numeric < low or numeric > high:
            self.logger.info("country %s outside [%s, %s]", numeric, low, high)
            self.stats["country_rejected"] += 1
            return False
        return True

    def normalize_country(self, data: dict) -> dict:
        """Normalize the country into its canonical form."""
        raw = data.get("country", "")
        cleaned = str(raw).strip().replace("-", "").replace(" ", "")
        if self.config.get("uppercase", True):
            cleaned = cleaned.upper()
        result = dict(data)
        result["country"] = cleaned
        result["country_normalized"] = True
        self.logger.debug("normalized country for %s", data.get("request_id"))
        self.stats["country_normalized"] += 1
        return result

    def log_country(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the country step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "country",
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
        for step in (self.validate_street, self.validate_postal_code, self.validate_city, self.validate_country,):
            step(request)
        return True
