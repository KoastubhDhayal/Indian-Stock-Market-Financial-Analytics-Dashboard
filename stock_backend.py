"""
Indian Stock Market Analytics Backend
Handles real-time data fetching, ML predictions, and investment recommendations
Integrated with FinBERT for sentiment analysis
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

# For production, install these packages:
# pip install yfinance nsepy pandas numpy scikit-learn tensorflow transformers torch

# Import FinBERT integration
try:
    from finbert_integration import FinBERTStockAnalyzer
    FINBERT_AVAILABLE = True
except ImportError:
    FINBERT_AVAILABLE = False
    print("FinBERT not available. Install with: pip install transformers torch")

class StockDataFetcher:
    """
    Fetches real-time stock data from Indian markets (NSE/BSE)
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 60  # seconds
        
    def fetch_live_data(self, symbol: str, exchange: str = "NSE") -> Dict:
        """
        Fetch live stock data with minimal latency
        
        Options for real data:
        1. NSE Official API (requires registration)
        2. yfinance library: symbol.NS for NSE, symbol.BO for BSE
        3. nsepy library for historical NSE data
        4. Alpha Vantage API
        5. WebSocket connections for true real-time data
        """
        
        # Example using yfinance (install: pip install yfinance)
        try:
            import yfinance as yf
            
            # Add .NS suffix for NSE stocks
            ticker_symbol = f"{symbol}.NS" if exchange == "NSE" else f"{symbol}.BO"
            ticker = yf.Ticker(ticker_symbol)
            
            # Get real-time data
            info = ticker.info
            history = ticker.history(period="1d", interval="1m")
            
            if not history.empty:
                latest = history.iloc[-1]
                prev_close = info.get('previousClose', latest['Close'])
                
                return {
                    'symbol': symbol,
                    'exchange': exchange,
                    'price': float(latest['Close']),
                    'change': float(latest['Close'] - prev_close),
                    'changePercent': float((latest['Close'] - prev_close) / prev_close * 100),
                    'volume': int(latest['Volume']),
                    'high': float(history['High'].max()),
                    'low': float(history['Low'].min()),
                    'open': float(history['Open'].iloc[0]),
                    'timestamp': datetime.now().isoformat(),
                    'marketCap': info.get('marketCap', 0),
                    'pe_ratio': info.get('trailingPE', None),
                    'eps': info.get('trailingEps', None),
                    'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh', None),
                    'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow', None),
                }
        except Exception as e:
            print(f"Error fetching data: {e}")
            # Fallback to simulated data
            return self._generate_simulated_data(symbol, exchange)
    
    def fetch_historical_data(self, symbol: str, days: int = 90, exchange: str = "NSE") -> pd.DataFrame:
        """
        Fetch historical data for analysis and ML training
        """
        try:
            import yfinance as yf
            
            ticker_symbol = f"{symbol}.NS" if exchange == "NSE" else f"{symbol}.BO"
            ticker = yf.Ticker(ticker_symbol)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            df = ticker.history(start=start_date, end=end_date)
            df['Returns'] = df['Close'].pct_change()
            df['MA_20'] = df['Close'].rolling(window=20).mean()
            df['MA_50'] = df['Close'].rolling(window=50).mean()
            
            return df
            
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return self._generate_simulated_historical_data(days)
    
    def _generate_simulated_data(self, symbol: str, exchange: str) -> Dict:
        """Fallback simulated data for testing"""
        base_price = np.random.uniform(500, 2000)
        change = np.random.uniform(-50, 50)
        
        return {
            'symbol': symbol,
            'exchange': exchange,
            'price': round(base_price, 2),
            'change': round(change, 2),
            'changePercent': round((change / base_price) * 100, 2),
            'volume': int(np.random.uniform(1000000, 10000000)),
            'high': round(base_price + abs(np.random.uniform(0, 30)), 2),
            'low': round(base_price - abs(np.random.uniform(0, 30)), 2),
            'open': round(base_price - np.random.uniform(-10, 10), 2),
            'timestamp': datetime.now().isoformat(),
        }
    
    def _generate_simulated_historical_data(self, days: int) -> pd.DataFrame:
        """Generate simulated historical data"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        prices = np.cumsum(np.random.randn(days) * 10) + 1000
        
        df = pd.DataFrame({
            'Date': dates,
            'Close': prices,
            'Open': prices + np.random.randn(days) * 5,
            'High': prices + abs(np.random.randn(days) * 10),
            'Low': prices - abs(np.random.randn(days) * 10),
            'Volume': np.random.randint(1000000, 10000000, days)
        })
        
        df['Returns'] = df['Close'].pct_change()
        df['MA_20'] = df['Close'].rolling(window=20).mean()
        df['MA_50'] = df['Close'].rolling(window=50).mean()
        
        return df


class TechnicalIndicators:
    """
    Calculate technical indicators for stock analysis
    """
    
    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> float:
        """Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1]) if not rsi.empty else 50.0
    
    @staticmethod
    def calculate_macd(data: pd.Series) -> Dict:
        """Moving Average Convergence Divergence"""
        ema_12 = data.ewm(span=12, adjust=False).mean()
        ema_26 = data.ewm(span=26, adjust=False).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        
        return {
            'macd': float(macd.iloc[-1]),
            'signal': float(signal.iloc[-1]),
            'histogram': float(histogram.iloc[-1])
        }
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.Series, period: int = 20) -> Dict:
        """Bollinger Bands"""
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        
        return {
            'upper': float(upper_band.iloc[-1]),
            'middle': float(sma.iloc[-1]),
            'lower': float(lower_band.iloc[-1]),
            'bandwidth': float((upper_band.iloc[-1] - lower_band.iloc[-1]) / sma.iloc[-1])
        }
    
    @staticmethod
    def calculate_stochastic_oscillator(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> Dict:
        """Stochastic Oscillator"""
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=3).mean()
        
        return {
            'k': float(k_percent.iloc[-1]),
            'd': float(d_percent.iloc[-1])
        }


class MLPredictor:
    """
    Machine Learning based price prediction and signal generation
    """
    
    def __init__(self):
        self.model = None
        
    def train_model(self, historical_data: pd.DataFrame):
        """
        Train ML model on historical data
        Uses ensemble of models: LSTM, Random Forest, XGBoost
        """
        # Feature engineering
        features = self._create_features(historical_data)
        
        # For production, implement proper ML pipeline:
        # 1. LSTM neural network for time series
        # 2. Random Forest for feature importance
        # 3. XGBoost for gradient boosting
        # 4. Ensemble voting mechanism
        
        return features
    
    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create ML features from raw data"""
        df = df.copy()
        
        # Technical features
        df['RSI'] = TechnicalIndicators.calculate_rsi(df['Close'])
        
        # Price momentum
        df['Momentum_1'] = df['Close'].pct_change(1)
        df['Momentum_5'] = df['Close'].pct_change(5)
        df['Momentum_10'] = df['Close'].pct_change(10)
        
        # Volume features
        df['Volume_Change'] = df['Volume'].pct_change()
        df['Volume_MA_20'] = df['Volume'].rolling(window=20).mean()
        
        # Volatility
        df['Volatility'] = df['Returns'].rolling(window=20).std()
        
        return df
    
    def predict_price(self, historical_data: pd.DataFrame, horizon: int = 1) -> Dict:
        """
        Predict future price with confidence interval
        
        Args:
            historical_data: Historical price data
            horizon: Number of days to predict ahead
        
        Returns:
            Prediction with confidence metrics
        """
        
        if len(historical_data) < 30:
            return None
        
        # Simple ensemble prediction (replace with actual ML models)
        recent_prices = historical_data['Close'].tail(20).values
        
        # Linear regression component
        x = np.arange(len(recent_prices))
        coeffs = np.polyfit(x, recent_prices, 1)
        trend = coeffs[0]
        
        # Moving average component
        ma_short = historical_data['Close'].tail(10).mean()
        ma_long = historical_data['Close'].tail(20).mean()
        ma_signal = 1 if ma_short > ma_long else -1
        
        # Current momentum
        momentum = historical_data['Returns'].tail(5).mean()
        
        # Weighted ensemble prediction
        current_price = recent_prices[-1]
        predicted_change = (trend * 0.4 + momentum * current_price * 0.3 + (ma_short - current_price) * 0.3)
        predicted_price = current_price + predicted_change * horizon
        
        # Confidence based on volatility and trend consistency
        volatility = historical_data['Returns'].tail(20).std()
        confidence = max(0.5, min(0.95, 1 - volatility * 10))
        
        # Prediction interval
        std_error = volatility * current_price * np.sqrt(horizon)
        
        return {
            'predicted_price': round(predicted_price, 2),
            'confidence': round(confidence, 3),
            'lower_bound': round(predicted_price - 1.96 * std_error, 2),
            'upper_bound': round(predicted_price + 1.96 * std_error, 2),
            'horizon_days': horizon,
            'signal': 'bullish' if predicted_price > current_price else 'bearish',
            'strength': abs(predicted_change / current_price)
        }


class InvestmentAdvisor:
    """
    Generate investment recommendations based on technical analysis,
    ML predictions, and risk assessment
    """
    
    def __init__(self):
        self.risk_profiles = {
            'conservative': {'max_loss': 0.05, 'confidence_threshold': 0.75},
            'moderate': {'max_loss': 0.10, 'confidence_threshold': 0.65},
            'aggressive': {'max_loss': 0.15, 'confidence_threshold': 0.55}
        }
    
    def generate_recommendation(
        self,
        current_data: Dict,
        prediction: Dict,
        technical_indicators: Dict,
        risk_profile: str = 'moderate',
        sentiment_data: Optional[Dict] = None
    ) -> Dict:
        """
        Generate comprehensive investment recommendation
        Now includes FinBERT sentiment analysis
        """
        
        profile = self.risk_profiles.get(risk_profile, self.risk_profiles['moderate'])
        
        # Scoring system
        scores = {
            'technical': self._score_technical(technical_indicators),
            'prediction': self._score_prediction(prediction, profile),
            'momentum': self._score_momentum(current_data),
            'risk': self._score_risk(current_data, technical_indicators)
        }
        
        # Add sentiment score if available
        if sentiment_data:
            scores['sentiment'] = self._score_sentiment(sentiment_data)
            # Adjust weights when sentiment is available
            overall_score = (
                scores['technical'] * 0.25 +
                scores['prediction'] * 0.30 +
                scores['momentum'] * 0.15 +
                scores['risk'] * 0.10 +
                scores['sentiment'] * 0.20
            )
        else:
            # Original weights without sentiment
            overall_score = (
                scores['technical'] * 0.3 +
                scores['prediction'] * 0.35 +
                scores['momentum'] * 0.2 +
                scores['risk'] * 0.15
            )
        
        # Generate recommendation
        if overall_score > 65 and prediction['confidence'] > profile['confidence_threshold']:
            action = 'STRONG BUY' if overall_score > 80 else 'BUY'
        elif overall_score < 35:
            action = 'STRONG SELL' if overall_score < 20 else 'SELL'
        else:
            action = 'HOLD'
        
        # Calculate targets
        current_price = current_data['price']
        target_price = prediction['predicted_price']
        
        # Risk management
        stop_loss = current_price * (1 - profile['max_loss'])
        take_profit = current_price + (target_price - current_price) * 1.5
        
        # Position sizing based on risk
        risk_reward_ratio = abs((target_price - current_price) / (current_price - stop_loss))
        position_size = self._calculate_position_size(
            overall_score, 
            risk_reward_ratio, 
            risk_profile
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(scores, prediction, technical_indicators, action, sentiment_data)
        
        return {
            'action': action,
            'overall_score': round(overall_score, 2),
            'target_price': round(target_price, 2),
            'stop_loss': round(stop_loss, 2),
            'take_profit': round(take_profit, 2),
            'position_size_percent': position_size,
            'risk_reward_ratio': round(risk_reward_ratio, 2),
            'time_horizon': f"{prediction['horizon_days']} days",
            'confidence': prediction['confidence'],
            'risk_level': self._assess_risk_level(scores['risk']),
            'reasoning': reasoning,
            'scores': scores,
            'sentiment_included': sentiment_data is not None
        }
    
    def _score_technical(self, indicators: Dict) -> float:
        """Score based on technical indicators"""
        score = 50  # Neutral baseline
        
        # RSI scoring
        rsi = indicators.get('rsi', 50)
        if rsi < 30:
            score += 20  # Oversold - bullish
        elif rsi > 70:
            score -= 20  # Overbought - bearish
        
        # MACD scoring
        macd = indicators.get('macd', {})
        if macd.get('histogram', 0) > 0:
            score += 15
        else:
            score -= 15
        
        # Bollinger Bands
        bb = indicators.get('bollinger_bands', {})
        if bb.get('bandwidth', 0.1) > 0.15:
            score += 10  # High volatility opportunity
        
        return max(0, min(100, score))
    
    def _score_prediction(self, prediction: Dict, profile: Dict) -> float:
        """Score based on ML prediction"""
        if not prediction:
            return 50
        
        confidence = prediction['confidence']
        strength = prediction.get('strength', 0)
        
        if prediction['signal'] == 'bullish':
            score = 50 + (confidence * 50)
        else:
            score = 50 - (confidence * 50)
        
        # Adjust for strength
        score += strength * 100 * 0.2
        
        return max(0, min(100, score))
    
    def _score_momentum(self, current_data: Dict) -> float:
        """Score based on price momentum"""
        change_percent = current_data.get('changePercent', 0)
        volume = current_data.get('volume', 0)
        
        score = 50
        
        # Price momentum
        if change_percent > 2:
            score += 25
        elif change_percent < -2:
            score -= 25
        else:
            score += change_percent * 10
        
        # Volume confirmation
        if volume > 5000000:
            score += 10
        
        return max(0, min(100, score))
    
    def _score_risk(self, current_data: Dict, indicators: Dict) -> float:
        """Score based on risk factors (higher is lower risk)"""
        score = 50
        
        # Volatility assessment
        rsi = indicators.get('rsi', 50)
        if 40 < rsi < 60:
            score += 20  # Stable range
        
        # Volume stability
        volume = current_data.get('volume', 0)
        if volume > 1000000:
            score += 15
        
        return max(0, min(100, score))
    
    def _score_sentiment(self, sentiment_data: Dict) -> float:
        """
        Score based on FinBERT sentiment analysis
        
        Args:
            sentiment_data: Results from FinBERT analysis
            
        Returns:
            Score from 0-100
        """
        if not sentiment_data:
            return 50
        
        overall = sentiment_data.get('overall_sentiment', {})
        sentiment = overall.get('overall_sentiment', 'neutral')
        score_value = overall.get('sentiment_score', 0.0)
        confidence = overall.get('confidence', 0.0)
        
        # Base score from sentiment
        if sentiment == 'positive':
            base_score = 50 + (score_value * 50)  # 50-100 range
        elif sentiment == 'negative':
            base_score = 50 + (score_value * 50)  # 0-50 range (score_value is negative)
        else:
            base_score = 50
        
        # Adjust by confidence
        final_score = base_score * confidence + 50 * (1 - confidence)
        
        # Bonus for momentum
        momentum = sentiment_data.get('sentiment_momentum', {})
        if momentum.get('trend') == 'improving':
            final_score += 10
        elif momentum.get('trend') == 'deteriorating':
            final_score -= 10
        
        return max(0, min(100, final_score))
    
    def _assess_risk_level(self, risk_score: float) -> str:
        """Assess overall risk level"""
        if risk_score > 70:
            return 'Low'
        elif risk_score > 40:
            return 'Medium'
        else:
            return 'High'
    
    def _calculate_position_size(self, score: float, risk_reward: float, risk_profile: str) -> float:
        """Calculate recommended position size as percentage of portfolio"""
        base_size = {
            'conservative': 5,
            'moderate': 10,
            'aggressive': 15
        }.get(risk_profile, 10)
        
        # Adjust based on score
        score_multiplier = score / 100
        
        # Adjust based on risk-reward
        rr_multiplier = min(risk_reward / 2, 1.5)
        
        position_size = base_size * score_multiplier * rr_multiplier
        
        return round(min(position_size, 25), 2)  # Cap at 25%
    
    def _generate_reasoning(self, scores: Dict, prediction: Dict, indicators: Dict, action: str, sentiment_data: Optional[Dict] = None) -> List[str]:
        """Generate human-readable reasoning"""
        reasoning = []
        
        # Technical analysis
        if scores['technical'] > 60:
            reasoning.append(f"Strong technical indicators (score: {scores['technical']:.0f}/100)")
        elif scores['technical'] < 40:
            reasoning.append(f"Weak technical setup (score: {scores['technical']:.0f}/100)")
        
        # ML prediction
        if prediction:
            conf_pct = prediction['confidence'] * 100
            reasoning.append(
                f"ML model predicts {prediction['signal']} movement with {conf_pct:.0f}% confidence"
            )
            
            price_change = abs(prediction['predicted_price'] - prediction.get('current_price', 0))
            if price_change > 0:
                reasoning.append(
                    f"Expected price target: ₹{prediction['predicted_price']:.2f}"
                )
        
        # FinBERT Sentiment
        if sentiment_data and 'sentiment' in scores:
            overall_sent = sentiment_data.get('overall_sentiment', {})
            sentiment = overall_sent.get('overall_sentiment', 'neutral')
            sent_confidence = overall_sent.get('confidence', 0.0) * 100
            
            reasoning.append(
                f"Market sentiment is {sentiment} with {sent_confidence:.0f}% confidence (FinBERT score: {scores['sentiment']:.0f}/100)"
            )
            
            # Add sentiment insights
            insights = sentiment_data.get('insights', [])
            if insights:
                reasoning.append(f"Sentiment insight: {insights[0]}")
        
        # RSI analysis
        rsi = indicators.get('rsi', 50)
        if rsi < 30:
            reasoning.append(f"RSI at {rsi:.1f} indicates oversold conditions")
        elif rsi > 70:
            reasoning.append(f"RSI at {rsi:.1f} indicates overbought conditions")
        
        # MACD
        macd = indicators.get('macd', {})
        if macd.get('histogram', 0) > 0:
            reasoning.append("MACD shows positive momentum")
        else:
            reasoning.append("MACD shows negative momentum")
        
        # Overall recommendation
        if action in ['BUY', 'STRONG BUY']:
            reasoning.append("Favorable entry point for long position")
        elif action in ['SELL', 'STRONG SELL']:
            reasoning.append("Consider reducing exposure or taking profits")
        else:
            reasoning.append("Wait for clearer signals before taking action")
        
        return reasoning


# Example usage
if __name__ == "__main__":
    # Initialize components
    fetcher = StockDataFetcher()
    predictor = MLPredictor()
    advisor = InvestmentAdvisor()
    
    # Fetch data for a stock
    symbol = "RELIANCE"
    
    print(f"Fetching data for {symbol}...")
    current_data = fetcher.fetch_live_data(symbol)
    historical_data = fetcher.fetch_historical_data(symbol, days=90)
    
    print(f"\nCurrent Price: ₹{current_data['price']}")
    print(f"Change: {current_data['change']} ({current_data['changePercent']:.2f}%)")
    
    # Calculate technical indicators
    print("\nCalculating technical indicators...")
    indicators = {
        'rsi': TechnicalIndicators.calculate_rsi(historical_data['Close']),
        'macd': TechnicalIndicators.calculate_macd(historical_data['Close']),
        'bollinger_bands': TechnicalIndicators.calculate_bollinger_bands(historical_data['Close'])
    }
    
    print(f"RSI: {indicators['rsi']:.2f}")
    print(f"MACD: {indicators['macd']}")
    
    # Generate prediction
    print("\nGenerating ML prediction...")
    prediction = predictor.predict_price(historical_data, horizon=1)
    
    if prediction:
        print(f"Predicted Price (1 day): ₹{prediction['predicted_price']}")
        print(f"Confidence: {prediction['confidence']*100:.1f}%")
        print(f"Signal: {prediction['signal'].upper()}")
    
    # Generate recommendation
    print("\nGenerating investment recommendation...")
    recommendation = advisor.generate_recommendation(
        current_data, 
        prediction, 
        indicators,
        risk_profile='moderate'
    )
    
    print(f"\n{'='*50}")
    print(f"RECOMMENDATION: {recommendation['action']}")
    print(f"{'='*50}")
    print(f"Overall Score: {recommendation['overall_score']}/100")
    print(f"Target Price: ₹{recommendation['target_price']}")
    print(f"Stop Loss: ₹{recommendation['stop_loss']}")
    print(f"Risk Level: {recommendation['risk_level']}")
    print(f"Position Size: {recommendation['position_size_percent']}% of portfolio")
    print(f"\nReasoning:")
    for i, reason in enumerate(recommendation['reasoning'], 1):
        print(f"{i}. {reason}")
