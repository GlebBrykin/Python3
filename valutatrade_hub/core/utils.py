def validate_amount(amount: float):
    if amount <= 0:
        raise ValueError("'amount' должен быть положительным числом")
    return True
