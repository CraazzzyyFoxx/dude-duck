from enum import StrEnum


class RouteTag(StrEnum):
    """Tags used to classify API routes"""

    BOOSTERS = "🤷🏿‍♀️‍ Boosters"
    ORDER_CHANNELS = "🧷 Telegram Channels"
    ORDER_MESSAGES = "✉️ Telegram Order Messages"
    ORDER_RENDERS = " 🔪 Order Render Templates"
    ORDERS = "📒 Orders"
    SHEETS_PARSERS = "📊 Google Sheets Parsers"
    TELEGRAM = "⛔️ Telegram Methods"
    SHEET = "🧲 Gather data from Google Sheets"
    