import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY')
DEFI_SAFETY_API_KEY = os.getenv('DEFI_SAFETY_API_KEY')

# API URLs
COINGECKO_API = "https://api.coingecko.com/api/v3"
COINGECKO_PRO_API = "https://pro-api.coingecko.com/api/v3" if COINGECKO_API_KEY else COINGECKO_API

# Bot settings
DEFAULT_CURRENCY = "usd"
SUPPORTED_CURRENCIES = ["usd", "eur", "gbp", "jpy", "aud", "cad", "chf", "cny", "inr", "brl"]

# Command descriptions
COMMANDS = {
    "start": "Show main menu",
    "help": "Show all available commands",
    "about": "About this bot",
    "price": "Get coin price (e.g., /price bitcoin)",
    "trending": "Show trending coins",
    "market": "Global market data",
    "search": "Search for a coin",
    "rugcheck": "Check token safety"
}

# Error messages
ERROR_MESSAGES = {
    "no_coin": "❌ Coin not found. Please try again.",
    "api_error": "❌ API error occurred. Please try later.",
    "invalid_input": "❌ Invalid input. Please check your command.",
    "contract_invalid": "❌ Invalid contract address format."
}
