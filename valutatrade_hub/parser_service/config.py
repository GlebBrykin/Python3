import os
from dataclasses import dataclass, field

from ..infra.settings import SettingsLoader


@dataclass
class ParserConfig:
    EXCHANGERATE_API_KEY: str = field(default_factory=lambda: os.getenv("EXCHANGERATE_API_KEY", "demo"))
    COINGECKO_URL: str = "https://api.coingecko.com/api/v3/simple/price"
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6"
    BASE_CURRENCY: str = "USD"
    FIAT_CURRENCIES: tuple = ("EUR", "GBP", "RUB")
    CRYPTO_CURRENCIES: tuple = ("BTC", "ETH", "SOL")
    CRYPTO_ID_MAP: dict = field(default_factory=lambda: {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana"})

    def __post_init__(self):
        settings = SettingsLoader()
        self.RATES_FILE_PATH = settings.RATES_FILE
        self.HISTORY_FILE_PATH = settings.HISTORY_FILE
        self.REQUEST_TIMEOUT = 10
