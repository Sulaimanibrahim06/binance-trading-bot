import logging
from decimal import Decimal, InvalidOperation

from binance.exceptions import BinanceAPIException, BinanceRequestException
from requests.exceptions import RequestException

from bot.client import BinanceFuturesClient


logger = logging.getLogger(__name__)


class OrderService:
    def __init__(self) -> None:
        self.client = BinanceFuturesClient()

    def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Decimal,
        price: Decimal | None = None,
        stop_price: Decimal | None = None,
    ) -> dict:
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": self._format_decimal(quantity),
        }

        if order_type == "LIMIT" and price is not None:
            params["price"] = self._format_decimal(price)
            params["timeInForce"] = "GTC"
        elif order_type == "STOP_LIMIT" and price is not None and stop_price is not None:
            params["type"] = "STOP"
            params["price"] = self._format_decimal(price)
            params["stopPrice"] = self._format_decimal(stop_price)
            params["timeInForce"] = "GTC"

        logger.info("API request: %s", params)

        try:
            response = self.client.place_order(**params)
            enriched_response = self._normalize_order_response(response)
            enriched_response = self._attach_avg_price(enriched_response)
            logger.info("API response: %s", enriched_response)
            return enriched_response
        except BinanceAPIException as exc:
            logger.exception("Binance API error while placing order")
            raise RuntimeError(
                f"Binance API error ({exc.status_code}): {exc.message}"
            ) from exc
        except BinanceRequestException as exc:
            logger.exception("Binance request error while placing order")
            raise RuntimeError(f"Binance request error: {exc.message}") from exc
        except RequestException as exc:
            logger.exception("Network failure while reaching Binance")
            raise RuntimeError(
                "Network failure while reaching Binance Futures Testnet."
            ) from exc
        except Exception as exc:
            logger.exception("Unexpected error while placing order")
            raise RuntimeError(f"Unexpected order failure: {exc}") from exc

    @staticmethod
    def _format_decimal(value: Decimal) -> str:
        return format(value.normalize(), "f")

    @staticmethod
    def _attach_avg_price(response: dict) -> dict:
        if response.get("avgPrice"):
            return response

        executed_qty = response.get("executedQty")
        cumulative_quote = response.get("cumQuote")

        try:
            if executed_qty and cumulative_quote and Decimal(executed_qty) > 0:
                avg_price = Decimal(cumulative_quote) / Decimal(executed_qty)
                response["avgPrice"] = format(avg_price.normalize(), "f")
        except (InvalidOperation, ZeroDivisionError):
            logger.debug("Could not calculate avgPrice from Binance response: %s", response)

        return response

    @staticmethod
    def _normalize_order_response(response: dict) -> dict:
        if "orderId" in response:
            return response

        if "algoId" in response:
            normalized = dict(response)
            normalized["orderId"] = response.get("algoId")
            normalized["status"] = response.get("algoStatus", "NEW")
            normalized["executedQty"] = response.get("executedQty", "0.0000")
            normalized["avgPrice"] = response.get("avgPrice", "0.00")
            return normalized

        return response
