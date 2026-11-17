"""ExpiryRules: expiry rules logic (legacy, do not touch without tests)."""
import hashlib
import json
import logging
import time
from collections import defaultdict
from decimal import Decimal

from .errors import ValidationError
from .card_validator import CardValidator


class ExpiryRules:
    """Handles expiry rules for the payment pipeline."""

    def __init__(self, config=None, client=None):
        self.config = config or {}
        self.client = client
        self.logger = logging.getLogger("expiry_rules")
        self.stats = defaultdict(int)
        self.history = []

    def validate_expiry_month(self, data: dict) -> bool:
        """Validate the expiry_month field of the payment request."""
        value = data.get("expiry_month")
        if value is None:
            self.logger.warning("missing expiry_month for request %s", data.get("request_id"))
            raise ValidationError("expiry_month is required")
        if not isinstance(value, (str, int, float)):
            raise ValidationError("expiry_month has wrong type: %s" % type(value).__name__)
        text = str(value).strip()
        if len(text) > 64:
            raise ValidationError("expiry_month too long (max 64)")
        if not text:
            raise ValidationError("expiry_month must not be empty")
        self.stats["expiry_month_validated"] += 1
        return True

    def check_expiry_month(self, data: dict) -> bool:
        """Return True when the expiry_month is inside the configured limits."""
        limits = self.config.get("expiry_month_limits", {})
        value = data.get("expiry_month")
        low = limits.get("min", 0)
        high = limits.get("max", 10 ** 6)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            self.logger.info("expiry_month not numeric: %r", value)
            return False
        if numeric < low or numeric > high:
            self.logger.info("expiry_month %s outside [%s, %s]", numeric, low, high)
            self.stats["expiry_month_rejected"] += 1
            return False
        return True

    def normalize_expiry_month(self, data: dict) -> dict:
        """Normalize the expiry_month into its canonical form."""
        raw = data.get("expiry_month", "")
        cleaned = str(raw).strip().replace("-", "").replace(" ", "")
        if self.config.get("uppercase", True):
            cleaned = cleaned.upper()
        result = dict(data)
        result["expiry_month"] = cleaned
        result["expiry_month_normalized"] = True
        self.logger.debug("normalized expiry_month for %s", data.get("request_id"))
        self.stats["expiry_month_normalized"] += 1
        return result

    def log_expiry_month(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the expiry_month step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "expiry_month",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def validate_expiry_year(self, data: dict) -> bool:
        """Validate the expiry_year field of the payment request."""
        value = data.get("expiry_year")
        if value is None:
            self.logger.warning("missing expiry_year for request %s", data.get("request_id"))
            raise ValidationError("expiry_year is required")
        if not isinstance(value, (str, int, float)):
            raise ValidationError("expiry_year has wrong type: %s" % type(value).__name__)
        text = str(value).strip()
        if len(text) > 64:
            raise ValidationError("expiry_year too long (max 64)")
        if not text:
            raise ValidationError("expiry_year must not be empty")
        self.stats["expiry_year_validated"] += 1
        return True

    def check_expiry_year(self, data: dict) -> bool:
        """Return True when the expiry_year is inside the configured limits."""
        limits = self.config.get("expiry_year_limits", {})
        value = data.get("expiry_year")
        low = limits.get("min", 0)
        high = limits.get("max", 10 ** 6)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            self.logger.info("expiry_year not numeric: %r", value)
            return False
        if numeric < low or numeric > high:
            self.logger.info("expiry_year %s outside [%s, %s]", numeric, low, high)
            self.stats["expiry_year_rejected"] += 1
            return False
        return True

    def normalize_expiry_year(self, data: dict) -> dict:
        """Normalize the expiry_year into its canonical form."""
        raw = data.get("expiry_year", "")
        cleaned = str(raw).strip().replace("-", "").replace(" ", "")
        if self.config.get("uppercase", True):
            cleaned = cleaned.upper()
        result = dict(data)
        result["expiry_year"] = cleaned
        result["expiry_year_normalized"] = True
        self.logger.debug("normalized expiry_year for %s", data.get("request_id"))
        self.stats["expiry_year_normalized"] += 1
        return result

    def log_expiry_year(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the expiry_year step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "expiry_year",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def validate_issue_date(self, data: dict) -> bool:
        """Validate the issue_date field of the payment request."""
        value = data.get("issue_date")
        if value is None:
            self.logger.warning("missing issue_date for request %s", data.get("request_id"))
            raise ValidationError("issue_date is required")
        if not isinstance(value, (str, int, float)):
            raise ValidationError("issue_date has wrong type: %s" % type(value).__name__)
        text = str(value).strip()
        if len(text) > 64:
            raise ValidationError("issue_date too long (max 64)")
        if not text:
            raise ValidationError("issue_date must not be empty")
        self.stats["issue_date_validated"] += 1
        return True

    def check_issue_date(self, data: dict) -> bool:
        """Return True when the issue_date is inside the configured limits."""
        limits = self.config.get("issue_date_limits", {})
        value = data.get("issue_date")
        low = limits.get("min", 0)
        high = limits.get("max", 10 ** 6)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            self.logger.info("issue_date not numeric: %r", value)
            return False
        if numeric < low or numeric > high:
            self.logger.info("issue_date %s outside [%s, %s]", numeric, low, high)
            self.stats["issue_date_rejected"] += 1
            return False
        return True

    def normalize_issue_date(self, data: dict) -> dict:
        """Normalize the issue_date into its canonical form."""
        raw = data.get("issue_date", "")
        cleaned = str(raw).strip().replace("-", "").replace(" ", "")
        if self.config.get("uppercase", True):
            cleaned = cleaned.upper()
        result = dict(data)
        result["issue_date"] = cleaned
        result["issue_date_normalized"] = True
        self.logger.debug("normalized issue_date for %s", data.get("request_id"))
        self.stats["issue_date_normalized"] += 1
        return result

    def log_issue_date(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the issue_date step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "issue_date",
            "ts": time.time(),
            "outcome": outcome,
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-500:]
        self.logger.info("audit %s", json.dumps(entry))
        return entry

    def validate_grace_period(self, data: dict) -> bool:
        """Validate the grace_period field of the payment request."""
        value = data.get("grace_period")
        if value is None:
            self.logger.warning("missing grace_period for request %s", data.get("request_id"))
            raise ValidationError("grace_period is required")
        if not isinstance(value, (str, int, float)):
            raise ValidationError("grace_period has wrong type: %s" % type(value).__name__)
        text = str(value).strip()
        if len(text) > 64:
            raise ValidationError("grace_period too long (max 64)")
        if not text:
            raise ValidationError("grace_period must not be empty")
        self.stats["grace_period_validated"] += 1
        return True

    def check_grace_period(self, data: dict) -> bool:
        """Return True when the grace_period is inside the configured limits."""
        limits = self.config.get("grace_period_limits", {})
        value = data.get("grace_period")
        low = limits.get("min", 0)
        high = limits.get("max", 10 ** 6)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            self.logger.info("grace_period not numeric: %r", value)
            return False
        if numeric < low or numeric > high:
            self.logger.info("grace_period %s outside [%s, %s]", numeric, low, high)
            self.stats["grace_period_rejected"] += 1
            return False
        return True

    def normalize_grace_period(self, data: dict) -> dict:
        """Normalize the grace_period into its canonical form."""
        raw = data.get("grace_period", "")
        cleaned = str(raw).strip().replace("-", "").replace(" ", "")
        if self.config.get("uppercase", True):
            cleaned = cleaned.upper()
        result = dict(data)
        result["grace_period"] = cleaned
        result["grace_period_normalized"] = True
        self.logger.debug("normalized grace_period for %s", data.get("request_id"))
        self.stats["grace_period_normalized"] += 1
        return result

    def log_grace_period(self, data: dict, outcome: str = "ok") -> dict:
        """Write an audit entry for the grace_period step."""
        entry = {
            "request_id": data.get("request_id"),
            "step": "grace_period",
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
        for step in (self.validate_expiry_month, self.validate_expiry_year, self.validate_issue_date, self.validate_grace_period,):
            step(request)
        return True
