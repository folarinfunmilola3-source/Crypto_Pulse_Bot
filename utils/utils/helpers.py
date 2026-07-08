import re
from typing import Optional

def format_price(price: float, currency: str = '$') -> str:
    """Format price with appropriate decimal places"""
    if price is None:
        return 'N/A'
    
    if price >= 1:
        return f"{currency}{price:,.2f}"
    elif price >= 0.01:
        return f"{currency}{price:,.4f}"
    else:
        return f"{currency}{price:.8f}"

def format_percentage(value: float) -> str:
    """Format percentage with sign and 2 decimals"""
    if value is None:
        return 'N/A'
    sign = '+' if value >= 0 else ''
    return f"{sign}{value:.2f}%"

def validate_address(address: str, chain: str = 'evm') -> bool:
    """Validate blockchain address format"""
    if chain.lower() in ['evm', 'eth', 'bsc', 'polygon']:
        # Ethereum-style address: 0x + 40 hex chars
        pattern = r'^0x[a-fA-F0-9]{40}$'
        return bool(re.match(pattern, address))
    elif chain.lower() == 'solana':
        # Solana address: base58 encoded, 32-44 chars
        pattern = r'^[1-9A-HJ-NP-Za-km-z]{32,44}$'
        return bool(re.match(pattern, address))
    return False

def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + '...'

def parse_coin_input(text: str) -> str:
    """Parse and clean coin input"""
    # Remove extra spaces and convert to lowercase
    return text.strip().lower()
