"""
Enhanced ML Prediction Model - Uses ensemble of models for better accuracy
Combines Random Forest, XGBoost-style boosting, and pattern recognition
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from datetime import datetime
from trading_engine import trading_engine
from config import MODEL_PARAMS


class EnhancedPricePredictor:
    """
    Ensemble ML model combining multiple algorithms for higher accuracy
    - Random Forest (handles non-linear patterns)
    - Gradient Boosting (captures complex interactions)
    - Logistic Regression (baseline probability)
    - Pattern Recognition (chart patterns)
    """

    def __init__(self):
        self.rf_model = None
        self.gb_model = None
        self.lr_model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.accuracy_metrics = {}

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare rich feature set for ML models
        """
        data = df.copy()

        required = ['RSI', 'MACD', 'MACD_Signal', 'BB_Upper', 'BB_Lower',
                   'Volume_Ratio', 'Close']
        for col in required:
            if col not in data.columns:
                return None

        # Bollinger Band position
        bb_range = data['BB_Upper'] - data['BB_Lower']
        data['BB_position'] = (data['Close'] - data['BB_Lower']) / bb_range.replace(0, 1)

        # Price returns at multiple timeframes
        data['Returns_1d'] = data['Close'].pct_change(1)
        data['Returns_3d'] = data['Close'].pct_change(3)
        data['Returns_7d'] = data['Close'].pct_change(7)

        # Volatility metrics
        data['Volatility_5d'] = data['Returns_1d'].rolling(5).std()
        data['Volatility_20d'] = data['Returns_1d'].rolling(20).std()

        # Moving average relationships
        data['SMA_ratio'] = data['Close'] / data['SMA_20']
        data['EMA_crossover'] = (data['EMA_12'] - data['EMA_26']) / data['Close']

        # RSI momentum
        data['RSI_momentum'] = data['RSI'].diff(3)

        # Volume-price relationship
        data['OBV'] = (np.sign(data['Close'].diff()) * data['Volume']).cumsum()
        data['OBV_sma'] = data['OBV'].rolling(20).mean()
        data['OBV_ratio'] = data['OBV'] / data['OBV_sma'].replace(0, 1)

        # Price patterns
        data['Higher_High'] = (data['High'] > data['High'].shift(1)).astype(int)
        data['Lower_Low'] = (data['Low'] < data['Low'].shift(1)).astype(int)
        data['Inside_Bar'] = ((data['High'] < data['High'].shift(1)) & (data['Low'] > data['Low'].shift(1))).astype(int)

        # Target: Will price go up in next 5 days?
        data['Future_Return_5d'] = data['Close'].shift(-5) / data['Close'] - 1
        data['Target'] = (data['Future_Return_5d'] > 0.01).astype(int)  # 1% threshold

        feature_cols = [
            'RSI', 'MACD', 'MACD_Signal', 'BB_position', 'Volume_Ratio',
            'Returns_1d', 'Returns_3d', 'Returns_7d',
            'Volatility_5d', 'Volatility_20d',
            'SMA_ratio', 'EMA_crossover', 'RSI_momentum',
            'OBV_ratio', 'Higher_High', 'Lower_Low', 'Inside_Bar'
        ]

        return data[feature_cols + ['Target']].dropna()

    def train(self, ticker: str = "SPY", period: str = "2y") -> dict:
        """Train the ensemble model on historical data"""
        try:
            # Get training data
            df = trading_engine.get_stock_data(ticker, period)
            if df is None or len(df) < 100:
                return {"success": False, "error": "Insufficient data"}

            df = trading_engine.calculate_indicators(df)
            features_df = self.prepare_features(df)

            if features_df is None or len(features_df) < 50:
                return {"success": False, "error": "Could not prepare features"}

            feature_cols = [c for c in features_df.columns if c != 'Target']
            X = features_df[feature_cols]
            y = features_df['Target']

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )

            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            # Train Random Forest
            self.rf_model = RandomForestClassifier(
                n_estimators=200, max_depth=12, min_samples_split=5,
                random_state=42, n_jobs=-1
            )
            self.rf_model.fit(X_train_scaled, y_train)

            # Train Gradient Boosting
            self.gb_model = GradientBoostingClassifier(
                n_estimators=150, max_depth=5, learning_rate=0.1,
                random_state=42
            )
            self.gb_model.fit(X_train_scaled, y_train)

            # Train Logistic Regression
            self.lr_model = LogisticRegression(max_iter=1000, random_state=42)
            self.lr_model.fit(X_train_scaled, y_train)

            # Evaluate each model
            rf_score = self.rf_model.score(X_test_scaled, y_test)
            gb_score = self.gb_model.score(X_test_scaled, y_test)
            lr_score = self.lr_model.score(X_test_scaled, y_test)

            # Ensemble accuracy
            rf_pred = self.rf_model.predict(X_test_scaled)
            gb_pred = self.gb_model.predict(X_test_scaled)
            lr_pred = self.lr_model.predict(X_test_scaled)

            # Majority vote
            ensemble_pred = np.round((rf_pred + gb_pred + lr_pred) / 3)
            ensemble_score = np.mean(ensemble_pred == y_test)

            self.is_trained = True
            self.feature_cols = feature_cols

            self.accuracy_metrics = {
                "rf_accuracy": round(rf_score * 100, 2),
                "gb_accuracy": round(gb_score * 100, 2),
                "lr_accuracy": round(lr_score * 100, 2),
                "ensemble_accuracy": round(ensemble_score * 100, 2)
            }

            return {
                "success": True,
                **self.accuracy_metrics,
                "samples_used": len(X_train),
                "ticker": ticker,
                "period": period
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def predict(self, df: pd.DataFrame) -> dict:
        """Make ensemble prediction"""
        if not self.is_trained:
            return {"prediction": "UNKNOWN", "confidence": 0}

        features_df = self.prepare_features(df)
        if features_df is None or len(features_df) < 5:
            return {"prediction": "UNKNOWN", "confidence": 0}

        X = features_df[self.feature_cols].iloc[-1:].values
        X_scaled = self.scaler.transform(X)

        # Get predictions from each model
        rf_proba = self.rf_model.predict_proba(X_scaled)[0]
        gb_proba = self.gb_model.predict_proba(X_scaled)[0]
        lr_proba = self.lr_model.predict_proba(X_scaled)[0]

        # Weighted ensemble (RF and GB weighted higher)
        ensemble_proba = (rf_proba * 0.4 + gb_proba * 0.4 + lr_proba * 0.2)

        prediction = "UP" if ensemble_proba[1] > 0.5 else "DOWN"
        confidence = max(ensemble_proba) * 100

        # Feature importance from RF
        importances = dict(zip(
            self.feature_cols,
            self.rf_model.feature_importances_
        ))
        top_features = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "prediction": prediction,
            "confidence": round(confidence, 1),
            "probability_up": round(ensemble_proba[1] * 100, 1),
            "probability_down": round(ensemble_proba[0] * 100, 1),
            "top_features": [{"name": f[0], "importance": round(f[1] * 100, 1)} for f in top_features],
            "model_votes": {
                "rf": "UP" if rf_proba[1] > 0.5 else "DOWN",
                "gb": "UP" if gb_proba[1] > 0.5 else "DOWN",
                "lr": "UP" if lr_proba[1] > 0.5 else "DOWN"
            }
        }

    def get_prediction_for_ticker(self, ticker: str) -> dict:
        """Get combined technical + ensemble ML prediction"""
        df = trading_engine.get_stock_data(ticker, period="3mo")
        if df is None:
            return {"error": f"Could not fetch data for {ticker}"}

        df = trading_engine.calculate_indicators(df)
        if df is None:
            return {"error": "Could not calculate indicators"}

        # Technical analysis
        ta_signal = trading_engine.generate_signals(df)

        # ML prediction
        ml_prediction = self.predict(df)

        # Combine signals
        bullish_score = 0
        bearish_score = 0

        if ta_signal['signal'] == 'BUY':
            bullish_score += ta_signal['confidence']
        elif ta_signal['signal'] == 'SELL':
            bearish_score += ta_signal['confidence']

        if ml_prediction.get('prediction') == 'UP':
            bullish_score += ml_prediction['confidence'] * 0.6
        elif ml_prediction.get('prediction') == 'DOWN':
            bearish_score += ml_prediction['confidence'] * 0.6

        if bullish_score > bearish_score + 30:
            recommendation = 'STRONG_BUY'
        elif bullish_score > bearish_score:
            recommendation = 'BUY'
        elif bearish_score > bullish_score + 30:
            recommendation = 'STRONG_SELL'
        elif bearish_score > bullish_score:
            recommendation = 'SELL'
        else:
            recommendation = 'HOLD'

        return {
            "ticker": ticker,
            "technical_signal": ta_signal,
            "ml_prediction": ml_prediction,
            "recommendation": recommendation,
            "bullish_score": bullish_score,
            "bearish_score": bearish_score,
            "current_price": df['Close'].iloc[-1],
            "accuracy_metrics": self.accuracy_metrics
        }


# Global instance
enhanced_predictor = EnhancedPricePredictor()