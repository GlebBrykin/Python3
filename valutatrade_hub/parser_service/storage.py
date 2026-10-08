import json
import os
import tempfile

from ..infra.settings import SettingsLoader


class RateStorage:
    def __init__(self):
        self.settings = SettingsLoader()

    def save_rates(self, pairs: dict):
        data = {"pairs": pairs, "last_refresh": list(pairs.values())[0]["updated_at"] if pairs else None}
        self._atomic_write(self.settings.RATES_FILE, data)

    def append_history(self, pairs: dict):
        if not os.path.exists(self.settings.HISTORY_FILE):
            history = []
        else:
            with open(self.settings.HISTORY_FILE, "r") as f:
                history = json.load(f)
        for pair, info in pairs.items():
            history.append(
                {
                    "id": f"{pair}_{info['updated_at']}",
                    "from_currency": pair.split("_")[0],
                    "to_currency": pair.split("_")[1],
                    "rate": info["rate"],
                    "timestamp": info["updated_at"],
                    "source": info["source"],
                }
            )
        self._atomic_write(self.settings.HISTORY_FILE, history)

    def _atomic_write(self, filepath, data):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(filepath))
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=4)
        os.replace(tmp, filepath)
