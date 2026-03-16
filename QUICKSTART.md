# Indian Stock Market Analytics Dashboard
## Complete AI-Powered Financial Analysis Platform

### 📦 Project Structure

```
indian-stock-analytics/
├── README.md                       # Complete documentation
├── FINBERT_GUIDE.md               # FinBERT sentiment analysis guide
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── start.sh                       # Quick start script
├── config.py                      # Configuration management
├── stock_backend.py               # Core ML & analytics engine
├── finbert_integration.py         # FinBERT sentiment analysis
├── api_server.py                  # REST API server (Flask)
└── indian_stock_dashboard.jsx     # React dashboard UI
```

### 🚀 Quick Start (5 Minutes)

#### Step 1: Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt
```

#### Step 2: Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (optional for testing)
nano .env
```

#### Step 3: Start the Server
```bash
# Make start script executable
chmod +x start.sh

# Run the server
./start.sh

# Or manually:
python3 api_server.py
```

#### Step 4: Access the Dashboard
- **API**: http://localhost:5000
- **Dashboard**: Copy `indian_stock_dashboard.jsx` to your React app or use as artifact in Claude

### 📊 Features Overview

✅ **Real-Time Data** - Live NSE/BSE stock prices with 5-second updates
✅ **ML Predictions** - LSTM + ensemble models for price forecasting
✅ **FinBERT Sentiment** - AI-powered news and social media analysis
✅ **Technical Indicators** - RSI, MACD, Bollinger Bands, Stochastic
✅ **Investment Advice** - Smart BUY/SELL/HOLD recommendations
✅ **Risk Management** - Stop-loss, take-profit, position sizing
✅ **Portfolio Tracking** - Multi-stock watchlist and analysis
✅ **RESTful API** - Easy integration with any frontend

### 🔑 Key Technologies

- **Backend**: Python 3.8+, Flask, pandas, numpy
- **ML/AI**: scikit-learn, TensorFlow, FinBERT (transformers)
- **Data**: yfinance (Yahoo Finance), nsepy (NSE India)
- **Frontend**: React, Recharts, Tailwind CSS
- **NLP**: FinBERT (ProsusAI), PyTorch, Transformers

### 📡 API Endpoints

```bash
# Health check
GET /api/health

# Live stock data
GET /api/stock/{symbol}

# Historical data
GET /api/stock/{symbol}/historical?days=90

# Technical indicators
GET /api/stock/{symbol}/indicators

# ML price prediction
GET /api/stock/{symbol}/prediction?horizon=1

# FinBERT sentiment analysis
GET /api/stock/{symbol}/sentiment?days=7

# Investment recommendation
GET /api/stock/{symbol}/recommendation?risk_profile=moderate

# Complete analysis (all-in-one)
GET /api/stock/{symbol}/complete

# Batch multiple stocks
POST /api/stocks/batch
Body: {"symbols": ["RELIANCE", "TCS", "INFY"]}

# Watchlist
GET /api/watchlist

# Sectors
GET /api/sectors
```

### 🎯 Example Usage

#### Python
```python
import requests

# Get complete analysis
response = requests.get('http://localhost:5000/api/stock/RELIANCE/complete')
data = response.json()

print(f"Price: ₹{data['data']['current']['price']}")
print(f"Recommendation: {data['data']['recommendation']['action']}")
print(f"Sentiment: {data['data']['sentiment']['overall']['overall_sentiment']}")
```

#### cURL
```bash
# Get recommendation with sentiment
curl "http://localhost:5000/api/stock/RELIANCE/recommendation?include_sentiment=true"

# Get sentiment analysis
curl "http://localhost:5000/api/stock/TCS/sentiment?days=7"
```

#### JavaScript/React
```javascript
fetch('http://localhost:5000/api/stock/RELIANCE/complete')
  .then(res => res.json())
  .then(data => {
    console.log('Stock:', data.data.current.symbol);
    console.log('Price:', data.data.current.price);
    console.log('Action:', data.data.recommendation.action);
  });
```

### 🔧 Configuration Options

Edit `config.py` or `.env` file:

- **API_PORT**: Server port (default 5000)
- **DEFAULT_EXCHANGE**: NSE or BSE (default NSE)
- **CACHE_DURATION**: Cache duration in seconds (default 60)
- **PREDICTION_HORIZON**: Days ahead to predict (default 1)
- **ENABLE_ML_PREDICTIONS**: Enable/disable ML (default True)
- **RSI_PERIOD**: RSI calculation period (default 14)
- **Risk Profiles**: Conservative, Moderate, Aggressive

### 📈 Popular Indian Stocks Supported

**Nifty 50**: RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK, HINDUNILVR, ITC, SBIN, BHARTIARTL, KOTAKBANK, LT, AXISBANK, ASIANPAINT, MARUTI, TITAN, SUNPHARMA, WIPRO, ULTRACEMCO, NESTLEIND, POWERGRID

**Bank Nifty**: HDFCBANK, ICICIBANK, SBIN, KOTAKBANK, AXISBANK, INDUSINDBK

**IT**: TCS, INFY, WIPRO, HCLTECH, TECHM

**Pharma**: SUNPHARMA, DRREDDY, CIPLA, DIVISLAB, BIOCON

Add `.NS` for NSE or `.BO` for BSE when using yfinance

### 🧪 Testing

```bash
# Test basic functionality
python3 stock_backend.py

# Test FinBERT
python3 finbert_integration.py

# Test API
python3 api_server.py
# Then visit http://localhost:5000/api/health
```

### 📚 Documentation

- **README.md** - Complete setup and usage guide
- **FINBERT_GUIDE.md** - FinBERT integration and sentiment analysis
- Inline code comments for all functions
- API endpoint documentation in api_server.py

### ⚙️ System Requirements

**Minimum**:
- Python 3.8+
- 4GB RAM
- 2GB disk space

**Recommended**:
- Python 3.10+
- 8GB RAM
- GPU (for faster FinBERT analysis)
- Redis (for caching)
- PostgreSQL (for data persistence)

### 🔐 Security Notes

- Never commit `.env` file with real API keys
- Use environment variables for sensitive data
- Enable rate limiting in production
- Use HTTPS in production
- Implement user authentication for multi-user deployment

### 🚀 Deployment Options

**Local Development**: 
```bash
python3 api_server.py
```

**Production (Gunicorn)**:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

**Docker**:
```bash
docker build -t stock-analytics .
docker run -p 5000:5000 stock-analytics
```

**Cloud**: AWS EC2, Google Cloud, Heroku, DigitalOcean

### 🐛 Troubleshooting

**Issue**: ModuleNotFoundError
```bash
pip install -r requirements.txt
```

**Issue**: FinBERT not loading
```bash
pip install transformers torch
```

**Issue**: No stock data
- Check internet connection
- Verify stock symbol is correct
- Try adding `.NS` suffix (e.g., RELIANCE.NS)

**Issue**: Slow performance
- Enable caching (Redis)
- Use GPU for FinBERT
- Reduce data fetch frequency

### 📊 Performance Tips

1. **Enable Caching**: Use Redis for 60-second cache
2. **Batch Requests**: Use `/api/stocks/batch` for multiple stocks
3. **GPU Acceleration**: Install CUDA for FinBERT speedup
4. **Async Processing**: Use Celery for background tasks
5. **CDN**: Use CloudFront for static assets

### 🔄 Updates & Maintenance

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Pull latest stock data
# (automatically handled by yfinance)

# Retrain ML models
# (implement your retraining schedule)
```

### 📞 Support & Resources

- **Documentation**: See README.md and FINBERT_GUIDE.md
- **Issues**: Check code comments and error messages
- **yfinance docs**: https://pypi.org/project/yfinance/
- **FinBERT paper**: https://arxiv.org/abs/1908.10063
- **Transformers docs**: https://huggingface.co/docs/transformers

### ⚠️ Legal Disclaimer

This software is for **educational and informational purposes only**. 

- Not financial advice
- Not investment recommendations
- Past performance doesn't guarantee future results
- Always do your own research
- Consult certified financial advisors
- Be aware of market risks
- Use at your own discretion

### 📄 License

MIT License - Free for commercial and personal use

### 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional data sources
- More ML models
- Better UI/UX
- Mobile app
- Real-time WebSocket updates
- Backtesting framework
- Options trading analysis

### 🎓 Learning Resources

- **Python**: https://docs.python.org/3/
- **Flask**: https://flask.palletsprojects.com/
- **React**: https://react.dev/
- **Machine Learning**: https://scikit-learn.org/
- **Technical Analysis**: https://www.investopedia.com/
- **FinBERT**: https://huggingface.co/ProsusAI/finbert

---

## 🎉 You're All Set!

Run `./start.sh` and start analyzing stocks with AI-powered insights!

**Built with ❤️ for Indian Stock Market Traders**

Version: 1.0.0 with FinBERT Integration
Last Updated: March 2026
