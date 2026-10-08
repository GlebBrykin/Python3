from abc import ABC, abstractmethod
from datetime import datetime, timezone

import requests

from ..core.exceptions import ApiRequestError
from .config import ParserConfig


class BaseApiClient(ABC):
    def __init__(self, config: ParserConfig):
        self.config = config

    @abstractmethod
    def fetch_rates(self) -> dict:
        pass


class CoinGeckoClient(BaseApiClient):
    def fetch_rates(self) -> dict:
        ids = ",".join([self.config.CRYPTO_ID_MAP[c] for c in self.config.CRYPTO_CURRENCIES])
        params = {"ids": ids, "vs_currencies": self.config.BASE_CURRENCY.lower()}
        try:
            resp = requests.get(self.config.COINGECKO_URL, params=params, timeout=self.config.REQUEST_TIMEOUT)
            if resp.status_code != 200:
                raise ApiRequestError(f"CoinGecko status {resp.status_code}")
            data = resp.json()
            result = {}
            for code in self.config.CRYPTO_CURRENCIES:
                cg_id = self.config.CRYPTO_ID_MAP[code]
                if cg_id in data and self.config.BASE_CURRENCY.lower() in data[cg_id]:
                    pair = f"{code}_{self.config.BASE_CURRENCY}"
                    result[pair] = {
                        "rate": data[cg_id][self.config.BASE_CURRENCY.lower()],
                        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                        "source": "CoinGecko",
                    }
            return result
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(f"CoinGecko network error: {e}")


class ExchangeRateApiClient(BaseApiClient):
    def fetch_rates(self) -> dict:
        url = (
            f"{self.config.EXCHANGERATE_API_URL}/{self.config.EXCHANGERATE_API_KEY}/latest/{self.config.BASE_CURRENCY}"
        )
        try:
            resp = requests.get(url, timeout=self.config.REQUEST_TIMEOUT)
            if resp.status_code != 200:
                raise ApiRequestError(f"ExchangeRate-API status {resp.status_code}")
            data = resp.json()
            if data.get("result") != "success":
                raise ApiRequestError(f"ExchangeRate-API error: {data.get('error-type', 'unknown')}")
            result = {}
            for code in self.config.FIAT_CURRENCIES:
                if code in data["conversion_rates"]:
                    rate_usd_to_fiat = data["conversion_rates"][code]
                    if rate_usd_to_fiat > 0:
                        rate_fiat_to_usd = 1.0 / rate_usd_to_fiat
                        pair = f"{code}_{self.config.BASE_CURRENCY}"
                        result[pair] = {
                            "rate": rate_fiat_to_usd,
                            "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                            "source": "ExchangeRate-API",
                        }
            return result
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(f"ExchangeRate-API network error: {e}")
