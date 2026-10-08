from abc import ABC, abstractmethod

from .exceptions import CurrencyNotFoundError


class Currency(ABC):
    def __init__(self, name: str, code: str):
        if not name:
            raise ValueError("Name cannot be empty")
        if not code or not (2 <= len(code) <= 5) or not code.isupper() or " " in code:
            raise ValueError("Invalid currency code")
        self.name = name
        self.code = code

    @abstractmethod
    def get_display_info(self) -> str:
        pass


class FiatCurrency(Currency):
    def __init__(self, name: str, code: str, issuing_country: str):
        super().__init__(name, code)
        self.issuing_country = issuing_country

    def get_display_info(self) -> str:
        return f"[FIAT] {self.code} — {self.name} (Issuing: {self.issuing_country})"


class CryptoCurrency(Currency):
    def __init__(self, name: str, code: str, algorithm: str, market_cap: float):
        super().__init__(name, code)
        self.algorithm = algorithm
        self.market_cap = market_cap

    def get_display_info(self) -> str:
        return f"[CRYPTO] {self.code} — {self.name} (Algo: {self.algorithm}, MCAP: {self.market_cap:.2e})"


_REGISTRY = {
    "USD": lambda: FiatCurrency("US Dollar", "USD", "United States"),
    "EUR": lambda: FiatCurrency("Euro", "EUR", "Eurozone"),
    "GBP": lambda: FiatCurrency("British Pound", "GBP", "United Kingdom"),
    "RUB": lambda: FiatCurrency("Russian Ruble", "RUB", "Russia"),
    "BTC": lambda: CryptoCurrency("Bitcoin", "BTC", "SHA-256", 1.12e12),
    "ETH": lambda: CryptoCurrency("Ethereum", "ETH", "Ethash", 3.5e11),
    "SOL": lambda: CryptoCurrency("Solana", "SOL", "Proof-of-History", 6.5e10),
}


def get_currency(code: str) -> "Currency":
    code = code.upper()
    if code not in _REGISTRY:
        raise CurrencyNotFoundError(code)
    return _REGISTRY[code]()
