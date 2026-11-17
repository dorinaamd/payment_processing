"""FraudRules: fraud rules logic (legacy, do not touch without tests)."""
import hashlib
import json
import logging
import time
from collections import defaultdict
from decimal import Decimal

from .errors import ValidationError
from .card_validator import CardValidator


class FraudRules:
    """Handles fraud rules for the payment pipeline."""

    def __init__(self, config=None, client=None):
        self.config = config or {}
        self.client = client
        self.logger = logging.getLogger("fraud_rules")
        self.stats = defaultdict(int)
        self.history = []

    def validate_velocity(self, data: dict) -> bool:
        """Validate the velocity field of the payment request."""
        value = data.get("velocity")
        if value is None:
            self.logger.warning("missing velocity for request %s", data.get("request_id"))
            raise ValidationError("velocity is required")
        if not isinstance(value, (str, int, float)):
            raise ValidationError("velocity has wrong type: %s" % type(value).__name__)
        text = str(value).strip()
        if len(text) > 64:
            raise ValidationError("velocity too long (max 64)")
        if not text:
            raise ValidationError("velocity must not be empty")
        self.stats["velocity_validated"] += 1
        return True

    def check_velocity(self, data: dict) -> bool:
        """Return True when the velocity is inside the configured limits."""
        limits = self.config.get("velocity_limits", {})
        value = data.get("velocity")
        low = limits.get("min", 0)
        high = limits.get("max", 10 ** 6)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            self.logger.info("velocity not numeric: %r", value)
            return False
        if numeric < low or numeric > high:
            self.logger.info("velocity %s outside [%s, %s]", numeric, low, high)
            self.stats["velocity_rejected"] += 1
            return False
        return True

    def normalize_velocity(self, data: dict) -> dict:
        """Normalize the velocity into its canonical form."""
        raw = data.get("velocity", "")
        cleaned = str(raw).strip().replace("-", "").replace(" ", "")
        if self.config.get("uppercase", True):
            cleaned = cleaned.upper()
        result = dict(data)
        result["velocity"] = cleaned
        result["velocity_normalized"] = True
        self.logger.debug("normalized velocity for %s", data.get("request_id"))
        self.stats["velocity_normalized"] += 1
        return result

    def log_velocity(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the velocity step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "velocity",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def validate_ip_address(self, data: dict) -> bool:
        """Validate the ip_address field of the payment request."""
        value = data.get("ip_address")
        if value is None:
            self.logger.warning("missing ip_address for request %s", data.get("request_id"))
            raise ValidationError("ip_address is required")
        if not isinstance(value, (str, int, float)):
            raise ValidationError("ip_address has wrong type: %s" % type(value).__name__)
        text = str(value).strip()
        if len(text) > 64:
            raise ValidationError("ip_address too long (max 64)")
        if not text:
            raise ValidationError("ip_address must not be empty")
        self.stats["ip_address_validated"] += 1
        return True

    def check_ip_address(self, data: dict) -> bool:
        """Return True when the ip_address is inside the configured limits."""
        limits = self.config.get("ip_address_limits", {})
        value = data.get("ip_address")
        low = limits.get("min", 0)
        high = limits.get("max", 10 ** 6)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            self.logger.info("ip_address not numeric: %r", value)
            return False
        if numeric < low or numeric > high:
            self.logger.info("ip_address %s outside [%s, %s]", numeric, low, high)
            self.stats["ip_address_rejected"] += 1
            return False
        return True

    def normalize_ip_address(self, data: dict) -> dict:
        """Normalize the ip_address into its canonical form."""
        raw = data.get("ip_address", "")
        cleaned = str(raw).strip().replace("-", "").replace(" ", "")
        if self.config.get("uppercase", True):
            cleaned = cleaned.upper()
        result = dict(data)
        result["ip_address"] = cleaned
        result["ip_address_normalized"] = True
        self.logger.debug("normalized ip_address for %s", data.get("request_id"))
        self.stats["ip_address_normalized"] += 1
        return result

    def log_ip_address(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the ip_address step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "ip_address",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def validate_device_id(self, data: dict) -> bool:
        """Validate the device_id field of the payment request."""
        value = data.get("device_id")
        if value is None:
            self.logger.warning("missing device_id for request %s", data.get("request_id"))
            raise ValidationError("device_id is required")
        if not isinstance(value, (str, int, float)):
            raise ValidationError("device_id has wrong type: %s" % type(value).__name__)
        text = str(value).strip()
        if len(text) > 64:
            raise ValidationError("device_id too long (max 64)")
        if not text:
            raise ValidationError("device_id must not be empty")
        self.stats["device_id_validated"] += 1
        return True

    def check_device_id(self, data: dict) -> bool:
        """Return True when the device_id is inside the configured limits."""
        limits = self.config.get("device_id_limits", {})
        value = data.get("device_id")
        low = limits.get("min", 0)
        high = limits.get("max", 10 ** 6)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            self.logger.info("device_id not numeric: %r", value)
            return False
        if numeric < low or numeric > high:
            self.logger.info("device_id %s outside [%s, %s]", numeric, low, high)
            self.stats["device_id_rejected"] += 1
            return False
        return True

    def normalize_device_id(self, data: dict) -> dict:
        """Normalize the device_id into its canonical form."""
        raw = data.get("device_id", "")
        cleaned = str(raw).strip().replace("-", "").replace(" ", "")
        if self.config.get("uppercase", True):
            cleaned = cleaned.upper()
        result = dict(data)
        result["device_id"] = cleaned
        result["device_id_normalized"] = True
        self.logger.debug("normalized device_id for %s", data.get("request_id"))
        self.stats["device_id_normalized"] += 1
        return result

    def log_device_id(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the device_id step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "device_id",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def validate_geo_location(self, data: dict) -> bool:
        """Validate the geo_location field of the payment request."""
        value = data.get("geo_location")
        if value is None:
            self.logger.warning("missing geo_location for request %s", data.get("request_id"))
            raise ValidationError("geo_location is required")
        if not isinstance(value, (str, int, float)):
            raise ValidationError("geo_location has wrong type: %s" % type(value).__name__)
        text = str(value).strip()
        if len(text) > 64:
            raise ValidationError("geo_location too long (max 64)")
        if not text:
            raise ValidationError("geo_location must not be empty")
        self.stats["geo_location_validated"] += 1
        return True

    def check_geo_location(self, data: dict) -> bool:
        """Return True when the geo_location is inside the configured limits."""
        limits = self.config.get("geo_location_limits", {})
        value = data.get("geo_location")
        low = limits.get("min", 0)
        high = limits.get("max", 10 ** 6)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            self.logger.info("geo_location not numeric: %r", value)
            return False
        if numeric < low or numeric > high:
            self.logger.info("geo_location %s outside [%s, %s]", numeric, low, high)
            self.stats["geo_location_rejected"] += 1
            return False
        return True

    def normalize_geo_location(self, data: dict) -> dict:
        """Normalize the geo_location into its canonical form."""
        raw = data.get("geo_location", "")
        cleaned = str(raw).strip().replace("-", "").replace(" ", "")
        if self.config.get("uppercase", True):
            cleaned = cleaned.upper()
        result = dict(data)
        result["geo_location"] = cleaned
        result["geo_location_normalized"] = True
        self.logger.debug("normalized geo_location for %s", data.get("request_id"))
        self.stats["geo_location_normalized"] += 1
        return result

    def log_geo_location(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the geo_location step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "geo_location",
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
        for step in (self.validate_velocity, self.validate_ip_address, self.validate_device_id, self.validate_geo_location,):
            step(request)
        return True
