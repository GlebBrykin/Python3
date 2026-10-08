import hashlib
import secrets
from datetime import datetime

from .exceptions import InsufficientFundsError


class User:
    def __init__(self, user_id: int, username: str, hashed_password: str, salt: str, registration_date: str):
        self._user_id = user_id
        self.username = username
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = (
            datetime.fromisoformat(registration_date) if isinstance(registration_date, str) else registration_date
        )

    @property
    def user_id(self):
        return self._user_id

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value: str):
        if not value or not isinstance(value, str):
            raise ValueError("Имя не может быть пустым")
        self._username = value

    @property
    def registration_date(self):
        return self._registration_date

    @property
    def hashed_password(self):
        return self._hashed_password

    @property
    def salt(self):
        return self._salt

    def verify_password(self, password: str) -> bool:
        return self._hashed_password == hashlib.sha256((password + self._salt).encode()).hexdigest()

    def change_password(self, new_password: str):
        if len(new_password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")
        self._salt = secrets.token_hex(8)
        self._hashed_password = hashlib.sha256((new_password + self._salt).encode()).hexdigest()

    def get_user_info(self) -> str:
        return (
            f"User ID: {self._user_id}, Username: {self._username}, Registered: {self._registration_date.isoformat()}"
        )

    def to_dict(self):
        return {
            "user_id": self._user_id,
            "username": self._username,
            "hashed_password": self._hashed_password,
            "salt": self._salt,
            "registration_date": self._registration_date.isoformat(),
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    @classmethod
    def create(cls, user_id: int, username: str, password: str):
        if len(password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")
        salt = secrets.token_hex(8)
        hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
        return cls(user_id, username, hashed_password, salt, datetime.now().isoformat())


class Wallet:
    def __init__(self, currency_code: str, balance: float = 0.0):
        self._currency_code = currency_code.upper()
        self.balance = balance

    @property
    def currency_code(self):
        return self._currency_code

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("Баланс должен быть числом")
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным")
        self._balance = float(value)

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        self.balance += amount

    def withdraw(self, amount: float):
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")
        if self.balance < amount:
            raise InsufficientFundsError(self.balance, amount, self._currency_code)
        self.balance -= amount

    def get_balance_info(self) -> str:
        return f"{self._currency_code}: {self._balance:.4f}"

    def to_dict(self):
        return {"currency_code": self._currency_code, "balance": self._balance}


class Portfolio:
    def __init__(self, user_id: int, wallets: dict = None):
        self._user_id = user_id
        self._wallets = {}
        if wallets:
            for code, w_data in wallets.items():
                if isinstance(w_data, dict):
                    self._wallets[code.upper()] = Wallet(w_data.get("currency_code", code), w_data.get("balance", 0.0))

    @property
    def user_id(self):
        return self._user_id

    @property
    def wallets(self):
        return dict(self._wallets)

    def add_currency(self, currency_code: str):
        code = currency_code.upper()
        if code not in self._wallets:
            self._wallets[code] = Wallet(code, 0.0)

    def get_wallet(self, currency_code: str) -> Wallet:
        return self._wallets.get(currency_code.upper())

    def get_total_value(self, base_currency: str, rates: dict) -> float:
        base_currency = base_currency.upper()
        total = 0.0
        for code, wallet in self._wallets.items():
            if code == base_currency:
                total += wallet.balance
            else:
                pair = f"{code}_{base_currency}"
                if pair in rates:
                    total += wallet.balance * rates[pair]["rate"]
        return total

    def to_dict(self):
        return {"user_id": self._user_id, "wallets": {code: w.to_dict() for code, w in self._wallets.items()}}

    @classmethod
    def from_dict(cls, data):
        return cls(data["user_id"], data.get("wallets", {}))
