"""
AI Trading App Configuration
"""
import os
from datetime import datetime, timedelta

# App Settings
APP_NAME = "TradeAI Pro"
APP_VERSION = "1.0.0"

# Trading Settings
INITIAL_BALANCE = 100_000  # Starting virtual cash (institutional-scale)
FREE_TRIAL_DAYS = 5  # Free trial period

# Pricing
PRICING = {
    "ai_signals_weekly": 9,
    "ai_signals_monthly": 36,  # ~$9/week * 4
    "newsletter_monthly": 19,
    "real_money_onboarding": 120,
    "real_money_onboarding_discounted": 99,  # For first-week registrants
    "gains_percentage": 10,  # 10% of gains bi-weekly
}

# Supported Tickers (default watchlist)
DEFAULT_TICKERS = [
    "AAPL", "GOOGL", "MSFT", "AMZN", "NVDA", "META", "TSLA", "AMD",
    "NFLX", "DIS", "SPY", "QQQ", "VTI", "IWM", "GLD", "BTC-USD"
]

# ML Model Settings
MODEL_PARAMS = {
    "n_estimators": 100,
    "max_depth": 10,
    "random_state": 42,
}

# Technical Analysis Settings
TA_CONFIGS = {
    "rsi_period": 14,
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
}

# UI Colors (High-tech theme)
THEME = {
    "primary": "#00D4FF",  # Cyan
    "secondary": "#7B2FFF",  # Purple
    "success": "#00FF88",  # Green
    "danger": "#FF4757",  # Red
    "warning": "#FFD93D",  # Yellow
    "background": "#0A0E17",  # Dark
    "card_bg": "#1A1F2E",  # Card background
    "text": "#E8E8E8",  # Light text
}

# Session/Cache Settings
CACHE_TTL = 300  # 5 minutes

# Alpaca Brokerage Integration
# ARMAC_ENCRYPTION_KEY: 32 url-safe base64 bytes. Generate with:
#   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Store in Streamlit secrets (for cloud) or .env (for local). NEVER commit.
ALPACA_PAPER_DEFAULT = True  # Start in paper mode — flip to False only after live testing
ALPACA_CONNECT_ENABLED = os.environ.get("ALPACA_CONNECT_ENABLED", "true").lower() == "true"
