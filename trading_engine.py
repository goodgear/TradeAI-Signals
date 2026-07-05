"""
Trading Engine - Data fetching and technical analysis
Manual implementation of TA indicators (no pandas-ta dependency)
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import TA_CONFIGS, DEFAULT_TICKERS


class TradingEngine:
    """Handles market data fetching and technical analysis"""

    def __init__(self):
        self.cache = {}
        self.cache_timeout = 60  # seconds

    def get_stock_data(self, ticker: str, period: str = "1mo") -> pd.DataFrame:
        """
        Fetch stock data from yfinance
        """
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)

            if df.empty:
                return None

            return df
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            return None

    def get_realtime_quote(self, ticker: str) -> dict:
        """Get real-time quote for a ticker"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.fast_info

            return {
                "symbol": ticker,
                "price": info.last_price,
                "change": info.last_price - info.previous_close,
                "change_pct": ((info.last_price - info.previous_close) / info.previous_close) * 100,
                "volume": info.last_volume,
                "market_cap": info.market_cap,
                "high": info.day_high,
                "low": info.day_low,
                "open": info.open,
                "previous_close": info.previous_close,
            }
        except:
            return None

    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI manually"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss.replace(0, 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """Calculate MACD manually"""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        macd_hist = macd - macd_signal
        return macd, macd_signal, macd_hist

    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2):
        """Calculate Bollinger Bands manually"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, sma, lower

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators manually
        """
        if df is None or df.empty:
            return None

        data = df.copy()

        # RSI
        data['RSI'] = self.calculate_rsi(data['Close'], period=TA_CONFIGS['rsi_period'])

        # MACD
        macd, macd_signal, macd_hist = self.calculate_macd(
            data['Close'],
            fast=TA_CONFIGS['macd_fast'],
            slow=TA_CONFIGS['macd_slow'],
            signal=TA_CONFIGS['macd_signal']
        )
        data['MACD'] = macd
        data['MACD_Signal'] = macd_signal
        data['MACD_Hist'] = macd_hist

        # Moving Averages
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['EMA_12'] = data['Close'].ewm(span=12, adjust=False).mean()
        data['EMA_26'] = data['Close'].ewm(span=26, adjust=False).mean()

        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(data['Close'])
        data['BB_Upper'] = bb_upper
        data['BB_Middle'] = bb_middle
        data['BB_Lower'] = bb_lower

        # ATR (Average True Range)
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift())
        low_close = np.abs(data['Low'] - data['Close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        data['ATR'] = tr.rolling(14).mean()

        # Stochastic Oscillator
        low_14 = data['Low'].rolling(14).min()
        high_14 = data['High'].rolling(14).max()
        data['Stoch_K'] = 100 * ((data['Close'] - low_14) / (high_14 - low_14).replace(0, 1e-10))
        data['Stoch_D'] = data['Stoch_K'].rolling(3).mean()

        # Volume analysis
        data['Volume_SMA'] = data['Volume'].rolling(20).mean()
        data['Volume_Ratio'] = data['Volume'] / data['Volume_SMA'].replace(0, 1)

        return data

    def generate_signals(self, df: pd.DataFrame) -> dict:
        """
        Generate buy/sell/hold signals based on technical indicators
        """
        if df is None or df.empty or 'RSI' not in df.columns:
            return {"signal": "HOLD", "confidence": 0, "reasons": []}

        latest = df.iloc[-1]
        signals = []
        confidence = 0

        # RSI Analysis
        if pd.notna(latest.get('RSI')):
            if latest['RSI'] < TA_CONFIGS['rsi_oversold']:
                signals.append(("BUY", 20, "RSI oversold"))
            elif latest['RSI'] > TA_CONFIGS['rsi_overbought']:
                signals.append(("SELL", 20, "RSI overbought"))

        # MACD Analysis
        if pd.notna(latest.get('MACD')) and pd.notna(latest.get('MACD_Signal')):
            if latest['MACD'] > latest['MACD_Signal'] and latest['MACD_Hist'] > 0:
                signals.append(("BUY", 25, "MACD bullish crossover"))
            elif latest['MACD'] < latest['MACD_Signal'] and latest['MACD_Hist'] < 0:
                signals.append(("SELL", 25, "MACD bearish crossover"))

        # Moving Average Crossover
        if pd.notna(latest.get('SMA_20')) and pd.notna(latest.get('SMA_50')):
            if latest['SMA_20'] > latest['SMA_50'] and latest['EMA_12'] > latest['EMA_26']:
                signals.append(("BUY", 15, "MA golden cross"))
            elif latest['SMA_20'] < latest['SMA_50'] and latest['EMA_12'] < latest['EMA_26']:
                signals.append(("SELL", 15, "MA death cross"))

        # Bollinger Bands
        if pd.notna(latest.get('BB_Lower')) and pd.notna(latest.get('BB_Upper')):
            if latest['Close'] < latest['BB_Lower']:
                signals.append(("BUY", 15, "Below lower Bollinger Band"))
            elif latest['Close'] > latest['BB_Upper']:
                signals.append(("SELL", 15, "Above upper Bollinger Band"))

        # Stochastic
        if pd.notna(latest.get('Stoch_K')):
            if latest['Stoch_K'] < 20 and latest['Stoch_D'] < 20:
                signals.append(("BUY", 10, "Stochastic oversold"))
            elif latest['Stoch_K'] > 80 and latest['Stoch_D'] > 80:
                signals.append(("SELL", 10, "Stochastic overbought"))

        # Volume spike
        if pd.notna(latest.get('Volume_Ratio')):
            if latest['Volume_Ratio'] > 2:
                signals.append(("BUY" if latest['MACD_Hist'] > 0 else "SELL", 15, "Volume spike"))

        # Aggregate signals
        buy_signals = [s for s in signals if s[0] == "BUY"]
        sell_signals = [s for s in signals if s[0] == "SELL"]

        total_buy = sum(s[1] for s in buy_signals)
        total_sell = sum(s[1] for s in sell_signals)

        if total_buy > total_sell and total_buy >= 40:
            final_signal = "BUY"
            confidence = min(total_buy, 95)
        elif total_sell > total_buy and total_sell >= 40:
            final_signal = "SELL"
            confidence = min(total_sell, 95)
        else:
            final_signal = "HOLD"
            confidence = 30 if total_buy == total_sell else abs(total_buy - total_sell)

        reasons = [s[2] for s in signals]

        return {
            "signal": final_signal,
            "confidence": confidence,
            "reasons": reasons,
            "indicators": {
                "rsi": latest.get('RSI', 0) if pd.notna(latest.get('RSI')) else 50,
                "macd": latest.get('MACD', 0) if pd.notna(latest.get('MACD')) else 0,
                "macd_signal": latest.get('MACD_Signal', 0) if pd.notna(latest.get('MACD_Signal')) else 0,
                "stoch_k": latest.get('Stoch_K', 50) if pd.notna(latest.get('Stoch_K')) else 50,
                "stoch_d": latest.get('Stoch_D', 50) if pd.notna(latest.get('Stoch_D')) else 50,
            }
        }

    def get_multiple_quotes(self, tickers: list) -> list:
        """Get quotes for multiple tickers"""
        quotes = []
        for ticker in tickers:
            quote = self.get_realtime_quote(ticker)
            if quote:
                quotes.append(quote)
        return quotes

    def scan_for_opportunities(self, tickers: list = None) -> list:
        """
        Scan multiple tickers for trading opportunities
        """
        if tickers is None:
            tickers = DEFAULT_TICKERS

        opportunities = []

        for ticker in tickers:
            df = self.get_stock_data(ticker, period="3mo")
            if df is not None:
                df_with_ta = self.calculate_indicators(df)
                signal_data = self.generate_signals(df_with_ta)

                if signal_data['signal'] in ['BUY', 'SELL']:
                    opportunities.append({
                        "ticker": ticker,
                        **signal_data,
                        "price": df['Close'].iloc[-1],
                        "change_1d": ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100 if len(df) > 1 else 0
                    })

        # Sort by confidence
        opportunities.sort(key=lambda x: x['confidence'], reverse=True)

        return opportunities


# Global instance
trading_engine = TradingEngine()
