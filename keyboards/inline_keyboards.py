from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu():
    """Create main menu with inline buttons"""
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

def get_price_menu():
    """Create price menu with popular coins"""
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
            InlineKeyboardButton("🔙 Back", callback_data='main_menu')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_menu():
    """Create back button"""
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='main_menu')]]
    return InlineKeyboardMarkup(keyboard)

def get_confirm_menu():
    """Create confirm/cancel menu"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data='confirm'),
            InlineKeyboardButton("❌ Cancel", callback_data='cancel')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
