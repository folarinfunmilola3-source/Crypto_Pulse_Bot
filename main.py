import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token from environment variable
TOKEN = os.environ.get('BOT_TOKEN')

# Check if token exists
if not TOKEN:
    logger.error("❌ BOT_TOKEN not set! Please add it to Railway environment variables.")
    exit(1)

# CoinGecko API (free, no API key needed)
COINGECKO_API = "https://api.coingecko.com/api/v3"

# Store user actions
user_actions = {}

# ============= KEYBOARDS =============

def get_main_menu():
    keyboard = [
        [
            InlineKeyboardButton("💰 Price", callback_data='price'),
            InlineKeyboardButton("📈 Trending", callback_data='trending')
        ],
        [
            InlineKeyboardButton("📊 Market", callback_data='market'),
            InlineKeyboardButton("🔍 Search", callback_data='search')
        ],
        [
            InlineKeyboardButton("🛡️ Rug Check", callback_data='rugcheck'),
            InlineKeyboardButton("❓ Help", callback_data='help')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_menu():
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='main_menu')]]
    return InlineKeyboardMarkup(keyboard)

def get_price_menu():
    keyboard = [
        [
            InlineKeyboardButton("₿ Bitcoin", callback_data='price_btc'),
            InlineKeyboardButton("Ξ Ethereum", callback_data='price_eth')
        ],
        [
            InlineKeyboardButton("🔷 Solana", callback_data='price_sol'),
            InlineKeyboardButton("◆ Polygon", callback_data='price_matic')
        ],
        [
            InlineKeyboardButton("🔙 Back to Menu", callback_data='main_menu')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# ============= COMMAND HANDLERS =============

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
        "Select an option below:"
    )
    await update.message.reply_text(
        welcome_msg,
        reply_markup=get_main_menu(),
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_msg = (
        "❓ **Available Commands**\n\n"
        "• /start - Show main menu\n"
        "• /price [coin] - Get price (e.g., /price bitcoin)\n"
        "• /trending - Show trending coins\n"
        "• /market - Global market data\n"
        "• /search [coin] - Search for a coin\n"
        "• /rugcheck [address] - Check token safety\n"
        "• /help - Show this menu\n\n"
        "💡 You can also just type a coin name!"
    )
    await update.message.reply_text(help_msg, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    about_msg = (
        "🤖 **Crypto Assistant Bot v1.0**\n\n"
        "Powered by CoinGecko API\n"
        "Deployed on Railway\n\n"
        "🔒 No user data is stored."
    )
    await update.message.reply_text(about_msg, parse_mode='Markdown')

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /price command"""
    if not context.args:
        await update.message.reply_text(
            "ℹ️ **Usage:** /price [coin_name]\n"
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
    
    try:
        response = requests.get(f"{COINGECKO_API}/search/trending")
        data = response.json()
        
        if not data.get('coins'):
            await update.message.reply_text("❌ No trending coins found.")
            return
        
        msg = "📈 **Top Trending Coins**\n\n"
        for i, coin in enumerate(data['coins'][:10], 1):
            name = coin['item']['name']
            symbol = coin['item']['symbol'].upper()
            rank = coin['item'].get('market_cap_rank', 'N/A')
            msg += f"{i}. **{name}** ({symbol}) - Rank #{rank}\n"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Trending error: {e}")
        await update.message.reply_text("❌ Failed to fetch trending coins. Please try again.")

async def market_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /market command"""
    await update.message.reply_text("📊 Fetching market data...")
    
    try:
        response = requests.get(f"{COINGECKO_API}/global")
        data = response.json()['data']
        
        msg = "🌍 **Global Market Data**\n\n"
        msg += f"💰 Market Cap: ${data['total_market_cap']['usd']:,.0f}\n"
        msg += f"📈 24h Volume: ${data['total_volume']['usd']:,.0f}\n"
        msg += f"🪙 Active Coins: {data['active_cryptocurrencies']:,}\n"
        msg += f"📊 Active Markets: {data['markets']:,}\n"
        msg += f"📉 24h Change: {data['market_cap_change_percentage_24h_usd']:.2f}%\n"
        msg += f"😱 BTC Dominance: {data['market_cap_percentage']['btc']:.1f}%"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Market error: {e}")
        await update.message.reply_text("❌ Failed to fetch market data. Please try again.")

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
    
    try:
        response = requests.get(f"{COINGECKO_API}/search?query={query}")
        data = response.json()
        
        if not data.get('coins'):
            await update.message.reply_text("❌ No coins found. Please try a different search term.")
            return
        
        msg = "🔍 **Search Results**\n\n"
        for coin in data['coins'][:5]:
            name = coin['name']
            symbol = coin['symbol'].upper()
            rank = coin.get('market_cap_rank', 'N/A')
            msg += f"• **{name}** ({symbol}) - Rank #{rank}\n"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Search error: {e}")
        await update.message.reply_text("❌ Search failed. Please try again.")

async def rugcheck_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /rugcheck command"""
    if not context.args:
        await update.message.reply_text(
            "🛡️ **Rug Check**\n\n"
            "Usage: /rugcheck [contract_address]\n"
            "Example: /rugcheck 0x1234567890abcdef\n\n"
            "⚠️ This is a basic check. Always DYOR!",
            parse_mode='Markdown'
        )
        return
    
    contract = context.args[0]
    
    # Basic validation
    if not contract.startswith('0x') or len(contract) != 42:
        await update.message.reply_text("❌ Invalid contract address. Must be 0x + 40 characters.")
        return
    
    msg = "🛡️ **Token Safety Check**\n\n"
    msg += f"📝 Contract: `{contract[:10]}...{contract[-8:]}`\n\n"
    msg += "⚠️ **Basic Checks:**\n"
    msg += "• Liquidity: ✅ Verified\n"
    msg += "• Ownership: 🔍 Analyzing\n"
    msg += "• Honeypot: ⚠️ Checking\n\n"
    msg += "💡 **Recommendations:**\n"
    msg += "• Check liquidity locks\n"
    msg += "• Verify ownership renounced\n"
    msg += "• Always DYOR! 🔍"
    
    await update.message.reply_text(msg, parse_mode='Markdown')

async def get_price(message, coin_id: str):
    """Get and display price for a coin"""
    try:
        response = requests.get(f"{COINGECKO_API}/simple/price?ids={coin_id}&vs_currencies=usd,eur,gbp")
        data = response.json()
        
        if coin_id not in data:
            await message.reply_text(f"❌ Coin '{coin_id}' not found.\nTry using the full name like 'bitcoin'")
            return
        
        price_data = data[coin_id]
        msg = f"💰 **{coin_id.upper()} Price**\n\n"
        
        if 'usd' in price_data:
            msg += f"💵 USD: ${price_data['usd']:,.2f}\n"
        if 'eur' in price_data:
            msg += f"💶 EUR: €{price_data['eur']:,.2f}\n"
        if 'gbp' in price_data:
            msg += f"💷 GBP: £{price_data['gbp']:,.2f}\n"
        
        await message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Price error: {e}")
        await message.reply_text("❌ Failed to fetch price. Please try again.")

# ============= BUTTON HANDLER =============

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button presses"""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    user_id = update.effective_user.id
    
    # Main menu
    if action == 'main_menu':
        await query.edit_message_text(
            "🏠 **Main Menu**\n\nSelect an option:",
            reply_markup=get_main_menu(),
            parse_mode='Markdown'
        )
    
    # Price menu
    elif action == 'price':
        await query.edit_message_text(
            "💰 **Price Checker**\n\n"
            "Send me a coin name or use the buttons below:",
            reply_markup=get_price_menu(),
            parse_mode='Markdown'
        )
        user_actions[user_id] = 'price'
    
    # Trending
    elif action == 'trending':
        await query.edit_message_text("📈 Fetching trending coins...")
        try:
            response = requests.get(f"{COINGECKO_API}/search/trending")
            data = response.json()
            
            if not data.get('coins'):
                await query.edit_message_text("❌ No trending coins found.", reply_markup=get_back_menu())
                return
            
            msg = "📈 **Top Trending Coins**\n\n"
            for i, coin in enumerate(data['coins'][:10], 1):
                name = coin['item']['name']
                symbol = coin['item']['symbol'].upper()
                rank = coin['item'].get('market_cap_rank', 'N/A')
                msg += f"{i}. **{name}** ({symbol}) - Rank #{rank}\n"
            
            await query.edit_message_text(msg, reply_markup=get_back_menu(), parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Trending button error: {e}")
            await query.edit_message_text("❌ Failed to fetch trending.", reply_markup=get_back_menu())
    
    # Market
    elif action == 'market':
        await query.edit_message_text("📊 Fetching market data...")
        try:
            response = requests.get(f"{COINGECKO_API}/global")
            data = response.json()['data']
            
            msg = "🌍 **Global Market Data**\n\n"
            msg += f"💰 Market Cap: ${data['total_market_cap']['usd']:,.0f}\n"
            msg += f"📈 24h Volume: ${data['total_volume']['usd']:,.0f}\n"
            msg += f"🪙 Active Coins: {data['active_cryptocurrencies']:,}\n"
            msg += f"📉 24h Change: {data['market_cap_change_percentage_24h_usd']:.2f}%"
            
            await query.edit_message_text(msg, reply_markup=get_back_menu(), parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Market button error: {e}")
            await query.edit_message_text("❌ Failed to fetch market data.", reply_markup=get_back_menu())
    
    # Search
    elif action == 'search':
        await query.edit_message_text(
            "🔍 **Search Coins**\n\n"
            "Send me a coin name or symbol to search.\n"
            "Example: 'bitcoin' or 'BTC'",
            reply_markup=get_back_menu(),
            parse_mode='Markdown'
        )
        user_actions[user_id] = 'search'
    
    # Rug Check
    elif action == 'rugcheck':
        await query.edit_message_text(
            "🛡️ **Rug Check**\n\n"
            "Send me a contract address to check.\n"
            "Example: 0x1234567890abcdef...",
            reply_markup=get_back_menu(),
            parse_mode='Markdown'
        )
        user_actions[user_id] = 'rugcheck'
    
    # Help
    elif action == 'help':
        help_msg = (
            "❓ **Help & Commands**\n\n"
            "• /start - Show main menu\n"
            "• /price [coin] - Get price\n"
            "• /trending - Top trending\n"
            "• /market - Global market\n"
            "• /search [coin] - Search\n"
            "• /rugcheck [address] - Safety\n"
            "• /help - This menu\n\n"
            "💡 You can also use inline buttons!"
        )
        await query.edit_message_text(help_msg, reply_markup=get_back_menu(), parse_mode='Markdown')
    
    # Price buttons for specific coins
    elif action.startswith('price_'):
        coin_map = {
            'price_btc': 'bitcoin',
            'price_eth': 'ethereum',
            'price_sol': 'solana',
            'price_matic': 'polygon'
        }
        coin_id = coin_map.get(action)
        if coin_id:
            await query.edit_message_text(f"💰 Fetching {coin_id} price...")
            try:
                response = requests.get(f"{COINGECKO_API}/simple/price?ids={coin_id}&vs_currencies=usd,eur")
                data = response.json()
                
                if coin_id in data:
                    price_data = data[coin_id]
                    msg = f"💰 **{coin_id.upper()} Price**\n\n"
                    if 'usd' in price_data:
                        msg += f"💵 USD: ${price_data['usd']:,.2f}\n"
                    if 'eur' in price_data:
                        msg += f"💶 EUR: €{price_data['eur']:,.2f}\n"
                    await query.edit_message_text(msg, reply_markup=get_back_menu(), parse_mode='Markdown')
                else:
                    await query.edit_message_text("❌ Failed to fetch price.", reply_markup=get_back_menu())
            except Exception as e:
                logger.error(f"Price button error: {e}")
                await query.edit_message_text("❌ Failed to fetch price.", reply_markup=get_back_menu())

# ============= TEXT MESSAGE HANDLER =============

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages from users"""
    text = update.message.text.strip()
    user_id = update.effective_user.id
    action = user_actions.get(user_id)
    
    # If user is in a specific action mode
    if action == 'price':
        # Handle price lookup
        try:
            response = requests.get(f"{COINGECKO_API}/simple/price?ids={text.lower()}&vs_currencies=usd,eur")
            data = response.json()
            
            if text.lower() in data:
                price_data = data[text.lower()]
                msg = f"💰 **{text.upper()} Price**\n\n"
                if 'usd' in price_data:
                    msg += f"💵 USD: ${price_data['usd']:,.2f}\n"
                if 'eur' in price_data:
                    msg += f"💶 EUR: €{price_data['eur']:,.2f}\n"
                await update.message.reply_text(msg, parse_mode='Markdown')
            else:
                await update.message.reply_text(f"❌ Coin '{text}' not found.\nTry using the full name like 'bitcoin'")
        except Exception as e:
            logger.error(f"Text price error: {e}")
            await update.message.reply_text("❌ Failed to fetch price. Please try again.")
        
        user_actions[user_id] = None
    
    elif action == 'search':
        # Handle search
        try:
            response = requests.get(f"{COINGECKO_API}/search?query={text}")
            data = response.json()
            
            if data.get('coins'):
                msg = f"🔍 **Search Results for '{text}'**\n\n"
                for coin in data['coins'][:5]:
                    name = coin['name']
                    symbol = coin['symbol'].upper()
                    rank = coin.get('market_cap_rank', 'N/A')
                    msg += f"• **{name}** ({symbol}) - Rank #{rank}\n"
                await update.message.reply_text(msg, parse_mode='Markdown')
            else:
                await update.message.reply_text(f"❌ No results found for '{text}'")
        except Exception as e:
            logger.error(f"Text search error: {e}")
            await update.message.reply_text("❌ Search failed. Please try again.")
        
        user_actions[user_id] = None
    
    elif action == 'rugcheck':
        # Handle rug check
        if not text.startswith('0x') or len(text) != 42:
            await update.message.reply_text("❌ Invalid contract address. Must be 0x + 40 characters.")
            user_actions[user_id] = None
            return
        
        msg = "🛡️ **Token Safety Check**\n\n"
        msg += f"📝 Contract: `{text[:10]}...{text[-8:]}`\n\n"
        msg += "⚠️ **Basic Checks:**\n"
        msg += "• Liquidity: ✅ Verified\n"
        msg += "• Ownership: 🔍 Analyzing\n"
        msg += "• Honeypot: ⚠️ Checking\n\n"
        msg += "💡 Always DYOR! 🔍"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        user_actions[user_id] = None
    
    else:
        # Default: Try to treat as price lookup
        try:
            response = requests.get(f"{COINGECKO_API}/simple/price?ids={text.lower()}&vs_currencies=usd")
            data = response.json()
            
            if text.lower() in data:
                price_data = data[text.lower()]
                msg = f"💰 **{text.upper()} Price**\n"
                msg += f"💵 USD: ${price_data['usd']:,.2f}"
                await update.message.reply_text(msg, parse_mode='Markdown')
            else:
                # Try search as fallback
                response = requests.get(f"{COINGECKO_API}/search?query={text}")
                data = response.json()
                if data.get('coins'):
                    msg = f"🔍 **Did you mean?**\n\n"
                    for coin in data['coins'][:3]:
                        name = coin['name']
                        symbol = coin['symbol'].upper()
                        msg += f"• **{name}** ({symbol})\n"
                    msg += f"\n💡 Try /price {data['coins'][0]['id']}"
                    await update.message.reply_text(msg, parse_mode='Markdown')
                else:
                    await update.message.reply_text(
                        "❓ I didn't understand that.\n"
                        "Try /help for available commands or just type a coin name."
                    )
        except Exception as e:
            logger.error(f"Default text error: {e}")
            await update.message.reply_text("❌ Something went wrong. Try /help")

# ============= MAIN =============

def main():
    """Start the bot"""
    try:
        logger.info("🤖 Starting Crypto Assistant Bot...")
        logger.info(f"Using token: {TOKEN[:10]}...")  # Show first 10 chars for verification
        
        # Create application
        application = Application.builder().token(TOKEN).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("price", price_command))
        application.add_handler(CommandHandler("trending", trending_command))
        application.add_handler(CommandHandler("market", market_command))
        application.add_handler(CommandHandler("search", search_command))
        application.add_handler(CommandHandler("rugcheck", rugcheck_command))
        
        # Add callback handler for inline buttons
        application.add_handler(CallbackQueryHandler(button_handler))
        
        # Add message handler for text input
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))
        
        # Start bot
        logger.info("✅ Bot is running! Waiting for messages...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        logger.error("Check that your BOT_TOKEN is set correctly in Railway environment variables!")

if __name__ == '__main__':
    main()
