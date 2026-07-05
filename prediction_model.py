"""
ML Prediction Model - Uses scikit-learn Random Forest
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from trading_engine import trading_engine
from config import MODEL_PARAMS


class PricePredictor:
    """
    ML model to predict short-term price movements
    Uses Random Forest classifier
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = [
            'RSI', 'MACD', 'MACD_Signal', 'BB_position',
            'Volume_Ratio', 'Returns_1d', 'Returns_3d', 'Volatility'
        ]
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for ML model
        
        Features:
        - RSI, MACD, MACD_Signal: Technical indicators
        - BB_position: Position within Bollinger Bands (0-1)
        - Volume_Ratio: Volume relative to average
        - Returns_1d, Returns_3d: Price returns
        - Volatility: Price volatility measure
        """
        data = df.copy()
        
        # Ensure all required columns exist
        required = ['RSI', 'MACD', 'MACD_Signal', 'BB_Upper', 'BB_Lower', 
                   'Volume_Ratio', 'Close']
        for col in required:
            if col not in data.columns:
                return None
        
        # Bollinger Band position (0 = at lower band, 1 = at upper band)
        bb_range = data['BB_Upper'] - data['BB_Lower']
        bb_position = (data['Close'] - data['BB_Lower']) / bb_range.replace(0, 1)
        data['BB_position'] = bb_position
        
        # Price returns
        data['Returns_1d'] = data['Close'].pct_change(1)
        data['Returns_3d'] = data['Close'].pct_change(3)
        
        # Volatility (rolling std)
        data['Volatility'] = data['Returns_1d'].rolling(5).std()
        
        # Create target variable (1 = price goes up next day, 0 = down or same)
        data['Target'] = (data['Close'].shift(-1) > data['Close']).astype(int)
        
        # Select features
        features_df = data[self.feature_names + ['Target']].dropna()
        
        return features_df
    
    def train(self, ticker: str = "SPY", period: str = "1y") -> dict:
        """
        Train the model on historical data
        
        Returns:
            Dict with training metrics
        """
        # Get data
        df = trading_engine.get_stock_data(ticker, period)
        if df is None:
            return {"success": False, "error": "Failed to fetch data"}
        
        # Calculate indicators
        df = trading_engine.calculate_indicators(df)
        if df is None:
            return {"success": False, "error": "Failed to calculate indicators"}
        
        # Prepare features
        features_df = self.prepare_features(df)
        if features_df is None or len(features_df) < 100:
            return {"success": False, "error": "Insufficient data"}
        
        # Split data
        X = features_df[self.feature_names]
        y = features_df['Target']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=MODEL_PARAMS['random_state']
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=MODEL_PARAMS['n_estimators'],
            max_depth=MODEL_PARAMS['max_depth'],
            random_state=MODEL_PARAMS['random_state'],
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        self.is_trained = True
        
        return {
            "success": True,
            "train_accuracy": round(train_score * 100, 2),
            "test_accuracy": round(test_score * 100, 2),
            "samples_used": len(X_train),
            "ticker": ticker,
            "period": period
        }
    
    def predict(self, df: pd.DataFrame) -> dict:
        """
        Make prediction on current data
        
        Returns:
            Dict with prediction and probability
        """
        if not self.is_trained or self.model is None:
            return {"prediction": "UNKNOWN", "confidence": 0, "reason": "Model not trained"}
        
        features_df = self.prepare_features(df)
        if features_df is None or len(features_df) < 10:
            return {"prediction": "UNKNOWN", "confidence": 0, "reason": "Insufficient data"}
        
        # Get latest row
        X = features_df[self.feature_names].iloc[-1:].values
        X_scaled = self.scaler.transform(X)
        
        # Predict
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        
        # Get feature importances for explanation
        importances = dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))
        
        top_features = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:3]
        
        result = {
            "prediction": "UP" if prediction == 1 else "DOWN",
            "confidence": round(max(probabilities) * 100, 1),
            "probability_up": round(probabilities[1] * 100, 1),
            "probability_down": round(probabilities[0] * 100, 1),
            "top_features": [{"name": f[0], "importance": round(f[1] * 100, 1)} for f in top_features],
            "indicators_used": dict(zip(self.feature_names, X[0].tolist()))
        }
        
        return result
    
    def get_prediction_for_ticker(self, ticker: str) -> dict:
        """
        Get prediction for a specific ticker
        
        Returns:
            Combined technical + ML prediction
        """
        # Get fresh data
        df = trading_engine.get_stock_data(ticker, period="3mo")
        if df is None:
            return {"error": f"Could not fetch data for {ticker}"}
        
        # Calculate indicators
        df = trading_engine.calculate_indicators(df)
        if df is None:
            return {"error": "Could not calculate indicators"}
        
        # Get technical signal
        ta_signal = trading_engine.generate_signals(df)
        
        # Get ML prediction
        ml_prediction = self.predict(df)
        
        # Combine signals
        combined = {
            "ticker": ticker,
            "technical_signal": ta_signal,
            "ml_prediction": ml_prediction,
            "current_price": df['Close'].iloc[-1],
            "timestamp": datetime.now().isoformat()
        }
        
        # Determine overall recommendation
        bullish_score = 0
        bearish_score = 0
        
        # Technical analysis weight
        if ta_signal['signal'] == 'BUY':
            bullish_score += ta_signal['confidence']
        elif ta_signal['signal'] == 'SELL':
            bearish_score += ta_signal['confidence']
        
        # ML prediction weight
        if ml_prediction.get('prediction') == 'UP':
            bullish_score += ml_prediction['confidence'] * 0.5
        elif ml_prediction.get('prediction') == 'DOWN':
            bearish_score += ml_prediction['confidence'] * 0.5
        
        if bullish_score > bearish_score + 20:
            combined['recommendation'] = 'STRONG_BUY'
        elif bullish_score > bearish_score:
            combined['recommendation'] = 'BUY'
        elif bearish_score > bullish_score + 20:
            combined['recommendation'] = 'STRONG_SELL'
        elif bearish_score > bullish_score:
            combined['recommendation'] = 'SELL'
        else:
            combined['recommendation'] = 'HOLD'
        
        combined['bullish_score'] = bullish_score
        combined['bearish_score'] = bearish_score
        
        return combined


# Global instance
predictor = PricePredictor()
