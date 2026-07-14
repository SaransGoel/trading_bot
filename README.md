# Binance Futures Testnet Trading Bot

A highly structured, interactive Python CLI application for placing and managing orders on the Binance Futures Testnet (USDT-M). 

This project demonstrates clean architecture, robust input validation, secure credential management, and an enhanced interactive user experience.

## Features
* **Core Order Types:** Place MARKET and LIMIT orders (BUY/SELL).
* **Bonus Order Types:** Place STOP_MARKET orders and automated Grid/Basket limit orders.
* **Order Management:** View active open orders, modify existing LIMIT orders, and cancel orders directly from the CLI.
* **Enhanced CLI UX:** Interactive menus, trade summary review screens, field-specific editing, and graceful resets (`Ctrl + C`) without crashing.
* **Robust Validation:** Strict input validation for symbols, order sides, pricing, and quantities.
* **Structured Logging:** Auto-rotating console and file-based logging for API requests, responses, and errors.

## Project Structure
```text
trading_bot/
│
├── bot/
│   ├── __init__.py        
│   ├── client.py          # Binance API wrapper and connection logic
│   ├── orders.py          # Order construction and execution logic
│   ├── validators.py      # Strict input validation functions
│   └── logging_config.py  # Structured logging configuration
│
├── logs/
│   └── trading_bot.log    # Auto-generated log file of API activity
│
├── cli.py                 # Main interactive CLI entry point
├── requirements.txt       # Project dependencies
├── .env                   # Secure environment variables (Not tracked in git)
└── README.md              # Project documentation
```

## Setup Steps

**1. Clone the repository and navigate to the project directory:**
```bash
git clone <your_repository_link>
cd trading_bot
```

**2. Create and activate a virtual environment:**
*   **Windows:**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```
*   **macOS/Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Configure Environment Variables:**
Create a `.env` file in the root directory (`trading_bot/`) and add your Binance Futures Testnet API credentials:
```env
BINANCE_TESTNET_API_KEY=your_api_key_here
BINANCE_TESTNET_API_SECRET=your_secret_key_here
```

## How to Run Examples

Start the interactive bot by running:
```bash
python cli.py
```

**Example 1: Placing a LIMIT Order**
1. Select option `1` from the Main Menu.
2. Enter the trading symbol (e.g., `BTCUSDT`).
3. Enter the side (`BUY` or `SELL`).
4. Enter the quantity (e.g., `0.01`).
5. Enter the order type (`LIMIT`).
6. Enter the target price (e.g., `60000`).
7. Review the order on the summary screen. Type `E` to execute.

**Example 2: Modifying an Open Order**
1. Select option `2` from the Main Menu.
2. Enter the symbol to search for active orders (e.g., `BTCUSDT`).
3. The CLI will display a list of your active orders with bracketed index numbers.
4. Type the index number `[0]` to select the order.
5. Enter the new target price. 
6. The bot will automatically modify the order queue on the exchange.

## Assumptions
*   **Testnet Only:** The bot is strictly hardcoded to route to `https://testnet.binancefuture.com/fapi`. It will not execute trades on the live Binance exchange.
*   **API Keys:** It is assumed the user has successfully generated Testnet-specific API keys from the Demo Trading dashboard, as live-platform keys will result in authentication errors.
*   **Limit Order Execution:** It is assumed all LIMIT orders require a Time-In-Force (TIF) of `GTC` (Good Till Canceled), which is hardcoded into the order manager.
*   **Asset Type:** Quantities are entered in the base asset amount (e.g., BTC), not the quote asset (USDT) notional value.