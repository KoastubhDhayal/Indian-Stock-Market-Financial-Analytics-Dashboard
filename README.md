# Indian Stock Market Financial Analytics Dashboard

A comprehensive real-time stock market analytics platform for NSE/BSE with AI-powered predictions and investment recommendations.

## 🚀 Features

### 1. **Real-Time Data with Negligible Latency**
- Live stock prices from NSE/BSE
- Auto-refresh every 5 seconds
- WebSocket support for instant updates
- Minimal latency data pipelines

### 2. **AI-Powered Predictions**
- Machine Learning price predictions
- LSTM neural networks for time series
- Ensemble models (Random Forest + XGBoost + LSTM)
- Confidence intervals and prediction bounds

### 3. **Investment Recommendations**
- Smart BUY/SELL/HOLD signals
- Risk-adjusted position sizing
- Stop-loss and take-profit targets
- Multiple risk profiles (Conservative, Moderate, Aggressive)

### 4. **Technical Analysis**
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Stochastic Oscillator
- Moving Averages (MA 20, MA 50, MA 200)

### 5. **Interactive Dashboard**
- Beautiful real-time charts
- Customizable watchlists
- Portfolio tracking
- Historical analysis
- Alert system

## 📋 Prerequisites

### Backend Requirements
```bash
Python 3.8+
pip install yfinance
pip install nsepy
pip install pandas
pip install numpy
pip install scikit-learn
pip install tensorflow  # For LSTM models
pip install flask  # For API server
pip install flask-cors
pip install redis  # For caching
```

### Frontend Requirements
```bash
Node.js 16+
React 18+
Recharts (included in artifact)
Tailwind CSS (included in artifact)
Lucide React icons (included in artifact)
```

## 🛠️ Setup Instructions

### 1. Backend Setup

#### Install Dependencies
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install yfinance nsepy pandas numpy scikit-learn tensorflow flask flask-cors redis
```

#### Run Backend Server
```bash
python stock_backend.py
```

### 2. Data Source Integration

#### Option A: Yahoo Finance (Free, Easy)
- Already integrated in `stock_backend.py`
- Add `.NS` suffix for NSE stocks
- Add `.BO` suffix for BSE stocks
- Example: `RELIANCE.NS`, `INFY.BO`

#### Option B: NSE Official API (Recommended for Production)
1. Register at https://www.nseindia.com/
2. Get API credentials
3. Update authentication in backend
4. Implement rate limiting and caching

#### Option C: Alpha Vantage (Free tier available)
1. Sign up at https://www.alphavantage.co/
2. Get free API key
3. 5 requests per minute on free tier
4. Add API key to backend configuration

#### Option D: NSEpy Library (Historical Data)
```python
from nsepy import get_history
from datetime import date

# Get historical data
stock_data = get_history(
    symbol="SBIN",
    start=date(2024, 1, 1),
    end=date(2024, 12, 31)
)
```

### 3. Frontend Setup

The dashboard is a React artifact that can run in Claude's interface. For production deployment:

```bash
# Create React app
npx create-react-app indian-stock-dashboard
cd indian-stock-dashboard

# Install dependencies
npm install recharts lucide-react

# Copy the component
# Copy indian_stock_dashboard.jsx to src/App.jsx

# Run development server
npm start
```

### 4. WebSocket for Real-Time Updates (Advanced)

For true real-time data with sub-second latency:

```python
# websocket_server.py
import asyncio
import websockets
import json
from stock_backend import StockDataFetcher

fetcher = StockDataFetcher()

async def stream_stock_data(websocket, path):
    """Stream real-time stock data to connected clients"""
    while True:
        data = fetcher.fetch_live_data("RELIANCE")
        await websocket.send(json.dumps(data))
        await asyncio.sleep(1)  # Update every second

start_server = websockets.serve(stream_stock_data, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
```

## 🎯 Usage Guide

### Basic Usage

1. **Select Stock**: Choose from popular Indian stocks in the dropdown
2. **View Live Data**: Price updates automatically every 5 seconds
3. **Check Recommendation**: AI provides BUY/SELL/HOLD signals
4. **Set Alerts**: Get notified of price targets
5. **Manage Watchlist**: Add stocks to track

### Advanced Features

#### 1. Custom Risk Profiles
```python
# In backend
recommendation = advisor.generate_recommendation(
    current_data,
    prediction,
    indicators,
    risk_profile='aggressive'  # Options: conservative, moderate, aggressive
)
```

#### 2. Multi-Stock Analysis
```python
# Analyze multiple stocks
stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK']
results = {}

for stock in stocks:
    data = fetcher.fetch_live_data(stock)
    historical = fetcher.fetch_historical_data(stock)
    prediction = predictor.predict_price(historical)
    results[stock] = prediction
```

#### 3. Portfolio Optimization
```python
# Calculate optimal portfolio weights
def optimize_portfolio(stocks, risk_tolerance):
    # Modern Portfolio Theory implementation
    # Sharpe ratio optimization
    # Risk-return tradeoff
    pass
```

## 📊 ML Model Details

### 1. Price Prediction Model

**Architecture**:
- LSTM layers for time series patterns
- Dense layers for feature combination
- Dropout for regularization

**Features**:
- Historical prices (OHLCV)
- Technical indicators (RSI, MACD, Bollinger Bands)
- Volume patterns
- Market sentiment
- Macroeconomic indicators

**Training**:
```python
# Model training example
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(lookback, n_features)),
    Dropout(0.2),
    LSTM(50, return_sequences=False),
    Dropout(0.2),
    Dense(25),
    Dense(1)
])

model.compile(optimizer='adam', loss='mse')
model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2)
```

### 2. Recommendation Engine

**Scoring System**:
- Technical Analysis: 30%
- ML Prediction: 35%
- Momentum: 20%
- Risk Assessment: 15%

**Decision Rules**:
- Score > 80: STRONG BUY
- Score 65-80: BUY
- Score 35-65: HOLD
- Score 20-35: SELL
- Score < 20: STRONG SELL

## 🔒 Security & Best Practices

### 1. API Key Management
```python
# Use environment variables
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('STOCK_API_KEY')
```

### 2. Rate Limiting
```python
from functools import lru_cache
from time import time

@lru_cache(maxsize=128)
def cached_fetch(symbol, timestamp):
    """Cache data for 60 seconds"""
    return fetcher.fetch_live_data(symbol)

# Use with current minute timestamp
data = cached_fetch('RELIANCE', int(time() // 60))
```

### 3. Error Handling
```python
try:
    data = fetcher.fetch_live_data(symbol)
except Exception as e:
    logger.error(f"Error fetching data: {e}")
    # Fallback to cached data or alternative source
    data = get_cached_data(symbol)
```

## 📈 Performance Optimization

### 1. Caching Strategy
```python
import redis

# Redis for caching
r = redis.Redis(host='localhost', port=6379, db=0)

def get_stock_data_cached(symbol):
    cached = r.get(f"stock:{symbol}")
    if cached:
        return json.loads(cached)
    
    data = fetcher.fetch_live_data(symbol)
    r.setex(f"stock:{symbol}", 60, json.dumps(data))  # Cache for 60 seconds
    return data
```

### 2. Database Setup (PostgreSQL)
```sql
CREATE TABLE stock_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20),
    price DECIMAL(10,2),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    volume BIGINT,
    INDEX idx_symbol_timestamp (symbol, timestamp)
);
```

### 3. Load Balancing
- Use multiple API sources as fallback
- Implement queue system for high traffic
- Use CDN for static assets

## 🧪 Testing

### Unit Tests
```python
import unittest

class TestStockFetcher(unittest.TestCase):
    def test_fetch_live_data(self):
        fetcher = StockDataFetcher()
        data = fetcher.fetch_live_data('RELIANCE')
        self.assertIn('price', data)
        self.assertGreater(data['price'], 0)

if __name__ == '__main__':
    unittest.main()
```

### Integration Tests
```python
def test_full_pipeline():
    # Fetch data
    data = fetcher.fetch_live_data('TCS')
    
    # Get historical data
    historical = fetcher.fetch_historical_data('TCS')
    
    # Generate prediction
    prediction = predictor.predict_price(historical)
    
    # Get recommendation
    recommendation = advisor.generate_recommendation(
        data, prediction, indicators
    )
    
    assert recommendation['action'] in ['BUY', 'SELL', 'HOLD']
```

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "stock_backend.py"]
```

### Cloud Deployment (AWS)
1. **EC2**: Deploy backend server
2. **RDS**: PostgreSQL database
3. **ElastiCache**: Redis for caching
4. **CloudFront**: CDN for frontend
5. **Lambda**: Serverless functions for predictions

### Monitoring
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_analytics.log'),
        logging.StreamHandler()
    ]
)

logger.info(f"Fetching data for {symbol}")
```

## 📱 Mobile App

For mobile deployment, consider:
- React Native version of dashboard
- Push notifications for alerts
- Offline mode with cached data
- Biometric authentication

## 🎓 Advanced Features to Add

1. **Sentiment Analysis**: Analyze news and social media
2. **Sector Analysis**: Compare stocks within sectors
3. **Backtesting**: Test strategies on historical data
4. **Options Analysis**: Greeks calculation for derivatives
5. **Fundamental Analysis**: P/E ratio, EPS, ROE analysis
6. **Global Correlation**: Track correlation with global markets
7. **Tax Optimization**: LTCG/STCG calculations
8. **Automated Trading**: Integration with broker APIs

## ⚠️ Disclaimer

This is a financial analytics tool for **educational and informational purposes only**. 

- Not financial advice
- Past performance doesn't guarantee future results
- Always do your own research
- Consult with a certified financial advisor
- Be aware of market risks

## 📄 License

MIT License - Feel free to use and modify for your needs.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues or questions:
- Check the documentation
- Review example code
- Test with simulated data first
- Ensure API credentials are correct

## 🔮 Roadmap

- [ ] Real-time WebSocket implementation
- [ ] Advanced ML models (Transformer architecture)
- [ ] Integration with broker APIs for automated trading
- [ ] Mobile app development
- [ ] Multi-language support
- [ ] Cryptocurrency support
- [ ] Options and derivatives analysis
- [ ] Portfolio rebalancing automation

---

**Built with ❤️ for Indian Stock Market Traders**
