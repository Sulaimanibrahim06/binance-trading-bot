import os

from binance.client import Client
from dotenv import load_dotenv


TESTNET_FUTURES_URL = "https://testnet.binancefuture.com/fapi"

load_dotenv()


class BinanceFuturesClient:
    def __init__(self) -> None:
        api_key = os.getenv("BINANCE_API_KEY")
        api_secret = os.getenv("BINANCE_API_SECRET")

        if not api_key or not api_secret:
            raise ValueError(
                "Missing Binance API credentials. Set BINANCE_API_KEY and BINANCE_API_SECRET in .env."
            )

        self.client = Client(api_key, api_secret, requests_params={"timeout": 10})
        self.client.FUTURES_URL = TESTNET_FUTURES_URL

    def place_order(self, **kwargs) -> dict:
        return self.client.futures_create_order(**kwargs)
