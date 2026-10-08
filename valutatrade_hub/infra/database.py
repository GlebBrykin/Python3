import json
import os
import tempfile

from ..core.models import Portfolio, User
from .settings import SettingsLoader


class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.settings = SettingsLoader()
        self._initialized = True

    def _atomic_write(self, filepath: str, data):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(filepath))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            os.replace(tmp_path, filepath)
        except Exception:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

    def _read_json(self, filepath: str):
        if not os.path.exists(filepath):
            return [] if "users" in filepath or "portfolios" in filepath else {}
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_users(self):
        return [User.from_dict(u) for u in self._read_json(self.settings.USERS_FILE)]

    def save_users(self, users: list):
        self._atomic_write(self.settings.USERS_FILE, [u.to_dict() for u in users])

    def load_portfolios(self):
        return {p["user_id"]: Portfolio.from_dict(p) for p in self._read_json(self.settings.PORTFOLIOS_FILE)}

    def save_portfolios(self, portfolios: dict):
        self._atomic_write(self.settings.PORTFOLIOS_FILE, [p.to_dict() for p in portfolios.values()])

    def load_rates(self):
        data = self._read_json(self.settings.RATES_FILE)
        if not data or "pairs" not in data:
            return {"pairs": {}, "last_refresh": None}
        return data

    def save_rates(self, rates_data: dict):
        self._atomic_write(self.settings.RATES_FILE, rates_data)
