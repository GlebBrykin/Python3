import os


class SettingsLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.DATA_DIR = "data"
        self.LOGS_DIR = "logs"
        self.USERS_FILE = os.path.join(self.DATA_DIR, "users.json")
        self.PORTFOLIOS_FILE = os.path.join(self.DATA_DIR, "portfolios.json")
        self.RATES_FILE = os.path.join(self.DATA_DIR, "rates.json")
        self.HISTORY_FILE = os.path.join(self.DATA_DIR, "exchange_rates.json")
        self.RATES_TTL_SECONDS = 300
        self.DEFAULT_BASE_CURRENCY = "USD"
        self.EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY", "demo")
        os.makedirs(self.DATA_DIR, exist_ok=True)
        os.makedirs(self.LOGS_DIR, exist_ok=True)
        self._initialized = True

    def get(self, key: str, default=None):
        return getattr(self, key.upper(), default)
