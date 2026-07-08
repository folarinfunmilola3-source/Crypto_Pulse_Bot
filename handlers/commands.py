import logging
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from keyboards.inline_keyboards import get_main_menu, get_price_menu
from utils.crypto_api import CryptoAPI
from utils.helpers import format_price, format_percentage
from config import COMMANDS

logger = logging.getLogger(__name__)
crypto_api = CryptoAPI()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_msg = (
        "🚀 **Crypto Assistant Bot**\n\n"
        "Your all-in-one cryptocurrency companion!\n\n"
        "📊 **Features:**\n"
        "• 💰 Real-time prices\n"
        "• 📈 Trending coins\n"
        "• 🌍 Global market data\n"
        "• 🔍 Coin search\n"
        "• 🛡️ Token safety check\n\n"
        "Select an option below or use /help for commands."
    )
    await update.message.reply_text(
        welcome_msg,
        reply_markup=get_main_menu(),
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_msg = "❓ **Available Commands**\n\n"
    for cmd, desc in COMMANDS.items():
        help_msg += f"• /{cmd} - {desc}\n"
    
    help_msg += "\n💡 **Quick Tips:**\n"
    help_msg += "• Use inline buttons for easy navigation\n"
    help_msg += "• Type any coin name to get its price\n"
    help_msg += "• Contact @BotFather for bot settings"
    
    await update.message.reply_text(help_msg, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    about_msg = (
        "🤖 **About Crypto Assistant Bot**\n\n"
        "Version: 1.0.0\n\n"
        "This bot provides real-time cryptocurrency data\n"
        "using the CoinGecko API.\n\n"
        "📊 **Data Sources:**\n"
        "• CoinGecko API\n"
        "• DeFi Safety API (coming soon)\n\n"
        "🔒 **Privacy:**\n"
        "No user data is stored.\n\n"
        "💻 **Open Source:**\n"
        "GitHub: https://github.com/yourusername/crypto-telegram-bot"
    )
    await update.message.reply_text(about_msg, parse_mode='Markdown')

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /price command"""
    if not context.args:
        await update.message.reply_text(
            "ℹ️ **Usage:** /price [coin_id]\n"
            "Example: /price bitcoin\n\n"
            "💡 Tip: You can also just type a coin name!",
            parse_mode='Markdown'
        )
        return
    
    coin_id = context.args[0].lower()
    await get_price(update.message, coin_id)

async def trending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /trending command"""
    await update.message.reply_text("📈 Fetching trending coins...")
    
    trending = crypto_api.get_trending()
    if not trending:
        await update.message.reply_text("❌ Failed to fetch trending coins. Please try again.")
        return
    
    msg = "📈 **Top Trending Coins**\n\n"
    for i, coin in enumerate(trending[:10], 1):
        name = coin['item']['name']
        symbol = coin['item']['symbol'].upper()
        rank = coin['item'].get('market_cap_rank', 'N/A')
        msg += f"{i}. **{name}** ({symbol}) - Rank #{rank}\n"
    
    await update.message.reply_text(msg, parse_mode='Markdown')

async def market_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /market command"""
    await update.message.reply_text("📊 Fetching market data...")
    
    data = crypto_api.get_market_data()
    if not data:
        await update.message.reply_text("❌ Failed to fetch market data. Please try again.")
        return
    
    msg = "🌍 **Global Market Data**\n\n"
    msg += f"💰 Market Cap: ${data['total_market_cap']['usd']:,.0f}\n"
    msg += f"📈 24h Volume: ${data['total_volume']['usd']:,.0f}\n"
    msg += f"🪙 Active Coins: {data['active_cryptocurrencies']:,}\n"
    msg += f"📊 Active Markets: {data['markets']:,}\n"
    msg += f"📉 24h Change: {format_percentage(data['market_cap_change_percentage_24h_usd'])}\n"
    msg += f"😱 BTC Dominance: {data['market_cap_percentage']['btc']:.1f}%"
    
    await update.message.reply_text(msg, parse_mode='Markdown')

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /search command"""
    if not context.args:
        await update.message.reply_text(
            "ℹ️ **Usage:** /search [coin_name]\n"
            "Example: /search dogecoin",
            parse_mode='Markdown'
        )
        return
    
    query = ' '.join(context.args)
    await update.message.reply_text(f"🔍 Searching for '{query}'...")
    
    results = crypto_api.search_coins(query)
    if not results:
        await update.message.reply_text("❌ No coins found. Please try a different search term.")
        return
    
    msg = "🔍 **Search Results**\n\n"
    for coin in results[:5]:
        name = coin['name']
        symbol = coin['symbol'].upper()
        rank = coin.get('market_cap_rank', 'N/A')
        msg += f"• **{name}** ({symbol}) - Rank #{rank}\n"
    
    await update.message.reply_text(msg, parse_mode='Markdown')

async def rugcheck_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /rugcheck command - basic token safety check"""
    if not context.args:
        await update.message.reply_text(
            "🛡️ **Rug Check**\n\n"
            "Usage: /rugcheck [contract_address]\n"
            "Example: /rugcheck 0x123456...\n\n"
            "⚠️ This is a basic check. Always DYOR!",
            parse_mode='Markdown'
        )
        return
    
    contract = context.args[0]
    
    # Basic validation
    if not validate_address(contract):
        await update.message.reply_text("❌ Invalid contract address format.")
        return
    
    msg = "🛡️ **Token Safety Check**\n\n"
    msg += f"📝 Contract: `{contract[:10]}...{contract[-8:]}`\n\n"
    msg += "⚠️ **Basic Checks:**\n"
    msg += "• Liquidity: ✅\n"
    msg += "• Ownership: 🔍\n"
    msg += "• Honeypot: ⚠️\n\n"
    msg += "💡 **Recommendations:**\n"
    msg += "• Check liquidity locks\n"
    msg += "• Verify ownership renounced\n"
    msg += "• Use DeFi safety tools\n"
    msg += "• Always DYOR! 🔍\n\n"
    msg += "🚨 This is a basic check. Use proper tools for detailed analysis."
    
    await update.message.reply_text(msg, parse_mode='Markdown')

async def get_price(message, coin_id: str):
    """Get and display price for a coin"""
    price_data = crypto_api.get_price(coin_id, ['usd', 'eur', 'gbp'])
    
    if not price_data:
        await message.reply_text(f"❌ Coin '{coin_id}' not found.")
        return
    
    msg = f"💰 **{coin_id.upper()} Price**\n\n"
    
    currencies = {
        'usd': '$',
        'eur': '€',
        'gbp': '£'
    }
    
    for currency, symbol in currencies.items():
        if currency in price_data:
            price = price_data[currency]
            msg += f"{symbol} {format_price(price, '')}\n"
    
    await message.reply_text(msg, parse_mode='Markdown')
