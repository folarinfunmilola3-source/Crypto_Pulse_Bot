import logging
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from keyboards.inline_keyboards import get_main_menu, get_price_menu, get_back_menu
from utils.crypto_api import CryptoAPI
from utils.helpers import format_price

logger = logging.getLogger(__name__)
crypto_api = CryptoAPI()

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button presses"""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    
    if action == 'main_menu':
        await query.edit_message_text(
            "🏠 **Main Menu**\n\nSelect an option:",
            reply_markup=get_main_menu(),
            parse_mode='Markdown'
        )
    
    elif action == 'price':
        await query.edit_message_text(
            "💰 **Price Checker**\n\n"
            "Send me a coin name or use the buttons below:",
            reply_markup=get_price_menu(),
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'price'
    
    elif action == 'trending':
        await query.edit_message_text("📈 Fetching trending coins...")
        trending = crypto_api.get_trending()
        
        if not trending:
            await query.edit_message_text(
                "❌ Failed to fetch trending coins. Please try again.",
                reply_markup=get_back_menu()
            )
            return
        
        msg = "📈 **Top Trending Coins**\n\n"
        for i, coin in enumerate(trending[:10], 1):
            name = coin['item']['name']
            symbol = coin['item']['symbol'].upper()
            rank = coin['item'].get('market_cap_rank', 'N/A')
            msg += f"{i}. **{name}** ({symbol}) - Rank #{rank}\n"
        
        await query.edit_message_text(msg, reply_markup=get_back_menu(), parse_mode='Markdown')
    
    elif action == 'market':
        await query.edit_message_text("📊 Fetching market data...")
        data = crypto_api.get_market_data()
        
        if not data:
            await query.edit_message_text(
                "❌ Failed to fetch market data.",
                reply_markup=get_back_menu()
            )
            return
        
        msg = "🌍 **Global Market Data**\n\n"
        msg += f"💰 Market Cap: ${data['total_market_cap']['usd']:,.0f}\n"
        msg += f"📈 24h Volume: ${data['total_volume']['usd']:,.0f}\n"
        msg += f"🪙 Active Coins: {data['active_cryptocurrencies']:,}\n"
        msg += f"📉 24h Change: {data['market_cap_change_percentage_24h_usd']:.2f}%"
        
        await query.edit_message_text(msg, reply_markup=get_back_menu(), parse_mode='Markdown')
    
    elif action == 'search':
        await query.edit_message_text(
            "🔍 **Search Coins**\n\n"
            "Send me a coin name or symbol to search.\n"
            "Example: 'bitcoin' or 'BTC'",
            reply_markup=get_back_menu(),
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'search'
    
    elif action == 'rugcheck':
        await query.edit_message_text(
            "🛡️ **Rug Check**\n\n"
            "Send me a contract address to check.\n"
            "Example: 0x1234567890abcdef...",
            reply_markup=get_back_menu(),
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'rugcheck'
    
    elif action == 'help':
        help_msg = "❓ **Help & Commands**\n\n"
        help_msg += "• /start - Show main menu\n"
        help_msg += "• /price [coin] - Get price\n"
        help_msg += "• /trending - Top trending\n"
        help_msg += "• /market - Global market\n"
        help_msg += "• /search [coin] - Search\n"
        help_msg += "• /rugcheck [address] - Safety\n"
        help_msg += "• /help - This menu\n"
        help_msg += "• /about - Bot info\n\n"
        help_msg += "💡 You can also use inline buttons!"
        
        await query.edit_message_text(help_msg, reply_markup=get_back_menu(), parse_mode='Markdown')

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages from users"""
    text = update.message.text
    action = context.user_data.get('action')
    
    if action == 'price':
        # Handle price lookup
        price_data = crypto_api.get_price(text.lower(), ['usd', 'eur'])
        if price_data:
            msg = f"💰 **{text.upper()} Price**\n\n"
            if 'usd' in price_data:
                msg += f"💵 USD: ${price_data['usd']:,.2f}\n"
            if 'eur' in price_data:
                msg += f"💶 EUR: €{price_data['eur']:,.2f}\n"
            await update.message.reply_text(msg, parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ Coin '{text}' not found.")
        
        context.user_data['action'] = None
    
    elif action == 'search':
        # Handle search
        results = crypto_api.search_coins(text)
        if results:
            msg = f"🔍 **Search Results for '{text}'**\n\n"
            for coin in results[:5]:
                name = coin['name']
                symbol = coin['symbol'].upper()
                rank = coin.get('market_cap_rank', 'N/A')
                msg += f"• **{name}** ({symbol}) - Rank #{rank}\n"
            await update.message.reply_text(msg, parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ No results found for '{text}'")
        
        context.user_data['action'] = None
    
    else:
        # Default: Try to treat as price lookup
        price_data = crypto_api.get_price(text.lower(), ['usd'])
        if price_data:
            msg = f"💰 **{text.upper()} Price**\n"
            msg += f"💵 USD: ${price_data['usd']:,.2f}"
            await update.message.reply_text(msg, parse_mode='Markdown')
        else:
            await update.message.reply_text(
                "❓ I didn't understand that.\n"
                "Try /help for available commands."
            )
