"""Sicherheits-Modul: PIN, Session-Timeout, Rate-Limit, Input-Sanitization."""
import time, re, hashlib
from typing import Optional, Dict
from memory.config_manager import ConfigManager
from memory.memory_manager import MemoryManager

class SecurityManager:
    def __init__(self):
        self.cfg = ConfigManager()
        self.memory = MemoryManager()
        self._sessions: Dict[str, float] = {}
        self._rate_limit: Dict[str, list] = {}
        self._pin_verified = False
        self._last_activity = time.time()

    def check_pin(self, pin: str) -> bool:
        stored = self.cfg.get("pin_code", "")
        if not stored or not self.cfg.get("pin_enabled", False):
            return True
        hashed = hashlib.sha256(pin.encode()).hexdigest()
        if hashed == stored:
            self._pin_verified = True
            self._last_activity = time.time()
            self.memory.audit("pin_success", "PIN erfolgreich eingegeben", "user")
            return True
        self.memory.audit("pin_fail", "Falsche PIN eingegeben", "user")
        return False

    def set_pin(self, pin: str) -> None:
        hashed = hashlib.sha256(pin.encode()).hexdigest()
        self.cfg.set("pin_code", hashed)
        self.cfg.set("pin_enabled", True)
        self.memory.audit("pin_set", "PIN wurde neu gesetzt", "user")

    def is_session_valid(self) -> bool:
        timeout = self.cfg.get("session_timeout", 30) * 60
        if time.time() - self._last_activity > timeout:
            self._pin_verified = False
            return False
        return True

    def touch(self):
        self._last_activity = time.time()

    def check_rate_limit(self, ip: str = "local", max_req: int = 60, window: int = 60) -> bool:
        now = time.time()
        if ip not in self._rate_limit:
            self._rate_limit[ip] = []
        self._rate_limit[ip] = [t for t in self._rate_limit[ip] if now - t < window]
        if len(self._rate_limit[ip]) >= max_req:
            return False
        self._rate_limit[ip].append(now)
        return True

    @staticmethod
    def sanitize_app_name(name: str) -> str:
        return re.sub(r"[^a-zA-Z0-9\s\.\-\_]", "", name).strip()

    @staticmethod
    def sanitize_url(url: str) -> Optional[str]:
        url = url.strip()
        if not url.startswith(("http://", "https://")): return None
        dangerous = ["file://", "ftp://", "dict://", "gopher://", "ldap://"]
        if any(url.lower().startswith(d) for d in dangerous): return None
        return url

    @staticmethod
    def is_dangerous_command(text: str) -> bool:
        dangerous = [";", "|", "&&", "||", "`", "$()", ">>", "<("]
        return any(d in text for d in dangerous)

    def require_confirmation(self, action: str) -> bool:
        if not self.cfg.get("confirmation_required", True): return False
        dangerous_actions = ["delete", "remove", "uninstall", "shutdown", "restart", "format", "rm -rf"]
        needs_confirm = any(d in action.lower() for d in dangerous_actions)
        if needs_confirm:
            self.memory.audit("confirmation_required", f"Bestaetigung angefordert fuer: {action[:100]}", "system")
        return needs_confirm
