# TradeAI Pro - AI-Powered Stock Trading Signal App

An AI-powered stock trading signal application with real-time market data, ML-based predictions, and a high-tech user interface.

## Features

- **Real-time Market Data** - Live stock prices via yfinance
- **AI Trading Signals** - Technical analysis + ML predictions
- **Paper Trading** - $10,000 fake money to practice
- **3-Day Free Trial** - No credit card required
- **High-Tech Interface** - Dark theme, responsive design
- **Auto-Trading Mode** - Let AI execute trades for you

## Tech Stack

- **UI**: Streamlit (Python web framework)
- **Data**: yfinance (Yahoo Finance API)
- **Technical Analysis**: pandas-ta (RSI, MACD, Bollinger Bands, etc.)
- **ML Prediction**: scikit-learn (Random Forest classifier)
- **Visualization**: Plotly (interactive charts)

## Installation

1. **Install Python 3.10+** from https://python.org

2. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Run the app**:
   ```powershell
   streamlit run app.py
   ```

## App Structure

```
ai_trading_app/
├── app.py              # Main Streamlit application
├── config.py           # Configuration settings
├── trading_engine.py   # Market data & technical analysis
├── prediction_model.py # ML prediction model
├── portfolio_manager.py# Portfolio & trade management
├── user_auth.py        # Authentication & subscriptions
└── requirements.txt    # Python dependencies
```

## Pricing

| Plan | Price | Features |
|------|-------|----------|
| Free Trial | 3 days | $10K fake money, all features |
| AI Signals | $9/week | Real-time buy/sell signals |
| Newsletter | $19/month | Market insights & education |
| Real Money | $120 + 10% gains | SEC-compliant trading |

## How It Works

1. **Register** - Enter name, email, password (free 3-day trial)
2. **Explore** - Search any ticker symbol
3. **Analyze** - View technical indicators & AI predictions
4. **Trade** - Buy/sell with fake money
5. **Subscribe** - Continue with paid plans after trial

## AI Model

The app uses a combination of:

1. **Technical Analysis** (pandas-ta):
   - RSI (Relative Strength Index)
   - MACD (Moving Average Convergence Divergence)
   - Bollinger Bands
   - Stochastic Oscillator
   - Moving Averages (SMA, EMA)

2. **Machine Learning** (scikit-learn):
   - Random Forest Classifier
   - Trained on historical price patterns
   - Combines 8 features for prediction

## Disclaimer

This app is for **educational purposes only**. The AI signals do not guarantee profits. Stock trading involves risk. Past performance does not indicate future results.

## Screenshots

The app features:
- Dark high-tech theme with cyan/purple accents
- Real-time stock charts with candlesticks
- AI signal badges (BUY/SELL/HOLD)
- Portfolio tracking with P/L display
- Responsive sidebar navigation
