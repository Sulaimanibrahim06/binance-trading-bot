import re
from decimal import Decimal, InvalidOperation


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9_]{5,20}$")


def validate_order_request(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None,
) -> dict:
    normalized_symbol = validate_symbol(symbol)
    normalized_side = validate_side(side)
    normalized_order_type = validate_order_type(order_type)
    normalized_quantity = validate_positive_decimal(quantity, "quantity")
    normalized_price = validate_price(normalized_order_type, price)

    return {
        "symbol": normalized_symbol,
        "side": normalized_side,
        "type": normalized_order_type,
        "quantity": normalized_quantity,
        "price": normalized_price,
    }


def validate_symbol(symbol: str) -> str:
    normalized_symbol = (symbol or "").strip().upper()
    if not normalized_symbol:
        raise ValueError("symbol is required")
    if not SYMBOL_PATTERN.fullmatch(normalized_symbol):
        raise ValueError("symbol must be an uppercase Binance symbol such as BTCUSDT")
    return normalized_symbol


def validate_side(side: str) -> str:
    normalized_side = (side or "").strip().upper()
    if normalized_side not in VALID_SIDES:
        raise ValueError("side must be BUY or SELL")
    return normalized_side


def validate_order_type(order_type: str) -> str:
    normalized_order_type = (order_type or "").strip().upper()
    if normalized_order_type not in VALID_ORDER_TYPES:
        raise ValueError("type must be MARKET or LIMIT")
    return normalized_order_type


def validate_positive_decimal(value: str, field_name: str) -> Decimal:
    try:
        decimal_value = Decimal(str(value).strip())
    except (InvalidOperation, AttributeError):
        raise ValueError(f"{field_name} must be a valid number") from None

    if decimal_value <= 0:
        raise ValueError(f"{field_name} must be greater than 0")
    return decimal_value


def validate_price(order_type: str, price: str | None) -> Decimal | None:
    if order_type == "LIMIT":
        if price is None:
            raise ValueError("price is required for LIMIT orders")
        return validate_positive_decimal(price, "price")

    if price is not None:
        raise ValueError("price can only be used with LIMIT orders")

    return None
