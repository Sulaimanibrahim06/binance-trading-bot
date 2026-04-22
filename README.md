# Binance Futures Testnet Trading Bot

Small Python CLI application for placing `MARKET` and `LIMIT` orders on the Binance Futures Testnet (USDT-M). The project is structured with a reusable Binance client layer, an order service layer, input validation, and file-based logging.

## Features

- Places `MARKET` and `LIMIT` orders on Binance Futures Testnet
- Supports both `BUY` and `SELL`
- Validates CLI input before sending requests
- Logs API requests, responses, and errors to `logs/trading.log`
- Handles invalid input, missing credentials, Binance API errors, and network failures
- Prints a clear request summary and response summary in the terminal

## Project Structure

```text
binance-trading-bot/
├── bot/
│   ├── __init__.py
│   ├── client.py
│   ├── logging_config.py
│   ├── orders.py
│   └── validators.py
├── cli.py
├── README.md
└── requirements.txt
```

## Requirements

- Python 3.10+
- Binance Futures Testnet account
- Binance Futures Testnet API key and secret

Testnet base URL used by the application:

`https://testnet.binancefuture.com`

## Setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:

```env
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
```

## How to Run

### MARKET order

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### LIMIT order

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000
```

### Help

```bash
python cli.py --help
```

## Example Output

```text
=== ORDER REQUEST ===
Symbol: BTCUSDT
Side: BUY
Type: MARKET
Quantity: 0.001

=== ORDER RESPONSE ===
Order ID: 123456789
Status: FILLED
Executed Qty: 0.001
Avg Price: 68421.50

SUCCESS: Order placed successfully.
```

## Logging

- Runtime log file: `logs/trading.log`
- The log captures request payloads, API responses, and stack traces for failures
- For submission, include copies of one successful `MARKET` order log and one successful `LIMIT` order log

## Assumptions

- The task is scoped to Binance Futures Testnet `USDT-M`
- Only `MARKET` and `LIMIT` orders are required for the core implementation
- `LIMIT` orders are sent with `timeInForce=GTC`
- The application assumes the account and symbol are enabled on the Futures Testnet

## Verification Performed

The following local checks were completed:

- CLI help command runs successfully
- Input validation catches malformed arguments before any API call
- Dependencies are installed in the local virtual environment

Live order placement requires valid Binance Futures Testnet credentials in `.env`.
