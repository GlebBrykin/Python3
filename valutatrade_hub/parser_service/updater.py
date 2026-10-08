import logging

from ..core.exceptions import ApiRequestError
from .api_clients import CoinGeckoClient, ExchangeRateApiClient
from .config import ParserConfig
from .storage import RateStorage


class RatesUpdater:
    def __init__(self):
        self.config = ParserConfig()
        self.storage = RateStorage()
        self.logger = logging.getLogger("valutatrade")

    def run_update(self, source: str = "all"):
        self.logger.info("Starting rates update...")
        combined_rates = {}
        errors = []
        if source in ("all", "coingecko"):
            try:
                self.logger.info("Fetching from CoinGecko...")
                cg = CoinGeckoClient(self.config)
                rates = cg.fetch_rates()
                combined_rates.update(rates)
                self.logger.info(f"OK ({len(rates)} rates)")
            except ApiRequestError as e:
                self.logger.error(f"Failed to fetch from CoinGecko: {e}")
                errors.append(str(e))
        if source in ("all", "exchangerate"):
            try:
                self.logger.info("Fetching from ExchangeRate-API...")
                er = ExchangeRateApiClient(self.config)
                rates = er.fetch_rates()
                combined_rates.update(rates)
                self.logger.info(f"OK ({len(rates)} rates)")
            except ApiRequestError as e:
                self.logger.error(f"Failed to fetch from ExchangeRate-API: {e}")
                errors.append(str(e))
        if combined_rates:
            self.storage.save_rates(combined_rates)
            self.storage.append_history(combined_rates)
            self.logger.info(f"Writing {len(combined_rates)} rates to cache...")
        if errors:
            raise ApiRequestError("Update completed with errors. Check logs.")
        return len(combined_rates)
