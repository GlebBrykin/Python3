from datetime import datetime, timedelta

from ..decorators import log_action
from ..infra.database import DatabaseManager
from ..infra.settings import SettingsLoader
from .currencies import get_currency
from .exceptions import ApiRequestError, CurrencyNotFoundError
from .models import Portfolio, User

db = DatabaseManager()
settings = SettingsLoader()


def get_current_user(username: str, password: str):
    users = db.load_users()
    for u in users:
        if u.username == username:
            if u.verify_password(password):
                return u
            raise ValueError("Неверный пароль")
    raise ValueError(f"Пользователь '{username}' не найден")


@log_action("REGISTER")
def register_user(username: str, password: str) -> User:
    users = db.load_users()
    for u in users:
        if u.username == username:
            raise ValueError(f"Имя пользователя '{username}' уже занято")
    user_id = max([u.user_id for u in users], default=0) + 1
    new_user = User.create(user_id, username, password)
    users.append(new_user)
    db.save_users(users)
    portfolios = db.load_portfolios()
    portfolios[user_id] = Portfolio(user_id)
    db.save_portfolios(portfolios)
    return new_user


@log_action("BUY")
def buy_currency(user_id: int, currency_code: str, amount: float):
    get_currency(currency_code)
    if amount <= 0:
        raise ValueError("'amount' должен быть положительным числом")
    portfolios = db.load_portfolios()
    if user_id not in portfolios:
        raise ValueError("Портфель не найден")
    portfolio = portfolios[user_id]
    portfolio.add_currency(currency_code)
    wallet = portfolio.get_wallet(currency_code)
    wallet.deposit(amount)
    db.save_portfolios(portfolios)
    rates = db.load_rates().get("pairs", {})
    rate_info = rates.get(f"{currency_code.upper()}_USD")
    rate_str = f"{rate_info['rate']:.2f}" if rate_info else "N/A"
    return wallet.balance, rate_str


@log_action("SELL")
def sell_currency(user_id: int, currency_code: str, amount: float):
    get_currency(currency_code)
    if amount <= 0:
        raise ValueError("'amount' должен быть положительным числом")
    portfolios = db.load_portfolios()
    if user_id not in portfolios:
        raise ValueError("Портфель не найден")
    portfolio = portfolios[user_id]
    wallet = portfolio.get_wallet(currency_code)
    if not wallet:
        raise ValueError(f"У вас нет кошелька '{currency_code.upper()}'.")
    wallet.withdraw(amount)
    db.save_portfolios(portfolios)
    rates = db.load_rates().get("pairs", {})
    rate_info = rates.get(f"{currency_code.upper()}_USD")
    rate_str = f"{rate_info['rate']:.2f}" if rate_info else "N/A"
    return wallet.balance, rate_str


def get_rate(from_code: str, to_code: str):
    get_currency(from_code)
    get_currency(to_code)
    rates_data = db.load_rates()
    pairs = rates_data.get("pairs", {})
    last_refresh = rates_data.get("last_refresh")
    pair_key = f"{from_code.upper()}_{to_code.upper()}"
    reverse_key = f"{to_code.upper()}_{from_code.upper()}"
    is_stale = True
    if last_refresh:
        try:
            last_dt = datetime.fromisoformat(last_refresh.replace("Z", "+00:00"))
            if datetime.now().astimezone() - last_dt < timedelta(seconds=settings.RATES_TTL_SECONDS):
                is_stale = False
        except: #noqa 722
            pass
    if is_stale:
        raise ApiRequestError("Данные устарели. Выполните 'update-rates'.")
    if pair_key in pairs:
        return pairs[pair_key]["rate"], pairs[pair_key]["updated_at"]
    elif reverse_key in pairs:
        return 1.0 / pairs[reverse_key]["rate"], pairs[reverse_key]["updated_at"]
    else:
        raise CurrencyNotFoundError(f"{from_code}→{to_code}")
