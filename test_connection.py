import os
from dotenv import load_dotenv
from bot.client import BinanceFuturesClient

# Load the keys from the .env file
load_dotenv()

if __name__ == "__main__":
    print("Testing connection to Binance Futures Testnet...")
    try:
        # This initializes your client layer and runs the ping test
        bot_client = BinanceFuturesClient()
        print("\n🎉 Connection Successful! Your environment and API keys are working perfectly.")
    except Exception as e:
        print(f"\n❌ Connection Failed. Error details: {e}")