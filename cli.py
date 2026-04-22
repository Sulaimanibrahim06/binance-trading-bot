import argparse
import logging
from decimal import Decimal

from bot.logging_config import setup_logging
from bot.orders import OrderService
from bot.validators import validate_order_request


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place Binance Futures Testnet orders from the command line.",
        epilog=(
            "Examples:\n"
            "  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001\n"
            "  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000\n"
            "  python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.001 --price 71000 --stop-price 70500"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, for example BTCUSDT")
    parser.add_argument("--side", required=True, help="Order side: BUY or SELL")
    parser.add_argument("--type", required=True, help="Order type: MARKET, LIMIT, or STOP_LIMIT")
    parser.add_argument("--quantity", required=True, help="Order quantity, for example 0.001")
    parser.add_argument("--price", help="Limit price. Required for LIMIT and STOP_LIMIT")
    parser.add_argument("--stop-price", help="Trigger price. Required for STOP_LIMIT")
    return parser


def print_order_request(
    symbol: str,
    side: str,
    order_type: str,
    quantity: Decimal,
    price: Decimal | None,
    stop_price: Decimal | None,
) -> None:
    print("\n=== ORDER REQUEST ===")
    print(f"Symbol: {symbol}")
    print(f"Side: {side}")
    print(f"Type: {order_type}")
    print(f"Quantity: {quantity}")
    if price is not None:
        print(f"Price: {price}")
    if stop_price is not None:
        print(f"Stop Price: {stop_price}")


def print_order_response(response: dict) -> None:
    print("\n=== ORDER RESPONSE ===")
    print(f"Order ID: {response.get('orderId', 'N/A')}")
    print(f"Status: {response.get('status', 'N/A')}")
    print(f"Executed Qty: {response.get('executedQty', 'N/A')}")
    print(f"Avg Price: {response.get('avgPrice') or 'N/A'}")


def main() -> int:
    log_path = setup_logging()
    logger = logging.getLogger(__name__)
    parser = build_parser()
    args = parser.parse_args()

    try:
        order_request = validate_order_request(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )

        print_order_request(
            symbol=order_request["symbol"],
            side=order_request["side"],
            order_type=order_request["type"],
            quantity=order_request["quantity"],
            price=order_request["price"],
            stop_price=order_request["stop_price"],
        )

        response = OrderService().create_order(
            symbol=order_request["symbol"],
            side=order_request["side"],
            order_type=order_request["type"],
            quantity=order_request["quantity"],
            price=order_request["price"],
            stop_price=order_request["stop_price"],
        )

        print_order_response(response)
        print(f"\nSUCCESS: Order placed successfully. Full logs: {log_path}")
        return 0

    except Exception as exc:
        logger.exception("CLI execution failed")
        print(f"\nFAILED: {exc}")
        print(f"Check logs for details: {log_path}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
