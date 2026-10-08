import argparse
import logging

from ..core import usecases
from ..core.exceptions import ApiRequestError, CurrencyNotFoundError, InsufficientFundsError
from ..infra.database import DatabaseManager
from ..logging_config import setup_logging
from ..parser_service.updater import RatesUpdater

logger = logging.getLogger("valutatrade")
db = DatabaseManager()


class CLI:
    def __init__(self):
        self.current_user = None

    def run(self):
        parser = argparse.ArgumentParser(description="ValutaTrade Hub CLI")
        subparsers = parser.add_subparsers(dest="command")
        reg_p = subparsers.add_parser("register")
        reg_p.add_argument("--username", required=True)
        reg_p.add_argument("--password", required=True)
        log_p = subparsers.add_parser("login")
        log_p.add_argument("--username", required=True)
        log_p.add_argument("--password", required=True)
        sp_p = subparsers.add_parser("show-portfolio")
        sp_p.add_argument("--base", default="USD")
        buy_p = subparsers.add_parser("buy")
        buy_p.add_argument("--currency", required=True)
        buy_p.add_argument("--amount", type=float, required=True)
        sell_p = subparsers.add_parser("sell")
        sell_p.add_argument("--currency", required=True)
        sell_p.add_argument("--amount", type=float, required=True)
        gr_p = subparsers.add_parser("get-rate")
        gr_p.add_argument("--from", dest="from_curr", required=True)
        gr_p.add_argument("--to", dest="to_curr", required=True)
        ur_p = subparsers.add_parser("update-rates")
        ur_p.add_argument("--source", default="all")
        sr_p = subparsers.add_parser("show-rates")
        sr_p.add_argument("--currency", default=None)
        args = parser.parse_args()
        if not args.command:
            parser.print_help()
            return
        try:
            if args.command == "register":
                user = usecases.register_user(args.username, args.password)
                print(f"Пользователь '{user.username}' зарегистрирован (id={user.user_id}).")
            elif args.command == "login":
                self.current_user = usecases.get_current_user(args.username, args.password)
                print(f"Вы вошли как '{self.current_user.username}'")
            elif args.command == "show-portfolio":
                if not self.current_user:
                    print("Сначала выполните login")
                    return
                portfolios = db.load_portfolios()
                p = portfolios.get(self.current_user.user_id)
                if not p or not p.wallets:
                    print("Портфель пуст.")
                    return
                rates = db.load_rates().get("pairs", {})
                print(f"Портфель пользователя '{self.current_user.username}' (база: {args.base}):")
                total = 0.0
                for code, w in p.wallets.items():
                    val = w.balance
                    if code != args.base.upper():
                        pair = f"{code}_{args.base.upper()}"
                        if pair in rates:
                            val *= rates[pair]["rate"]
                    total += val
                    print(f"- {code}: {w.balance:.4f}  → {val:.2f} {args.base}")
                print("-" * 30)
                print(f"ИТОГО: {total:,.2f} {args.base}")
            elif args.command == "buy":
                if not self.current_user:
                    print("Сначала выполните login")
                    return
                new_bal, rate = usecases.buy_currency(self.current_user.user_id, args.currency, args.amount)
                print(
                    f"Покупка выполнена: {args.amount:.4f} {args.currency.upper()} по курсу {rate} USD/{args.currency.upper()}"
                )
                print(f"Новый баланс: {new_bal:.4f} {args.currency.upper()}")
            elif args.command == "sell":
                if not self.current_user:
                    print("Сначала выполните login")
                    return
                new_bal, rate = usecases.sell_currency(self.current_user.user_id, args.currency, args.amount)
                print(
                    f"Продажа выполнена: {args.amount:.4f} {args.currency.upper()} по курсу {rate} USD/{args.currency.upper()}"
                )
                print(f"Новый баланс: {new_bal:.4f} {args.currency.upper()}")
            elif args.command == "get-rate":
                rate, updated = usecases.get_rate(args.from_curr, args.to_curr)
                print(f"Курс {args.from_curr}→{args.to_curr}: {rate:.8f} (обновлено: {updated})")
                print(f"Обратный курс {args.to_curr}→{args.from_curr}: {1 / rate:.8f}")
            elif args.command == "update-rates":
                updater = RatesUpdater()
                count = updater.run_update(args.source)
                print(f"Update successful. Total rates updated: {count}.")
            elif args.command == "show-rates":
                rates_data = db.load_rates()
                pairs = rates_data.get("pairs", {})
                if not pairs:
                    print("Локальный кеш курсов пуст. Выполните 'update-rates'.")
                    return
                print(f"Rates from cache (updated at {rates_data.get('last_refresh', 'N/A')}):")
                for pair, info in pairs.items():
                    if args.currency and args.currency.upper() not in pair:
                        continue
                    print(f"- {pair}: {info['rate']}")
        except InsufficientFundsError as e:
            print(e)
        except CurrencyNotFoundError as e:
            print(e)
        except ApiRequestError as e:
            print(f"Ошибка API: {e}")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            logger.exception("Unexpected error")
            print(f"Непредвиденная ошибка: {e}")


def main():
    setup_logging()
    cli = CLI()
    cli.run()
