"""
Flask API Server for Stock Analytics
Provides REST endpoints for the React dashboard
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from stock_backend import (
    StockDataFetcher, 
    TechnicalIndicators, 
    MLPredictor, 
    InvestmentAdvisor
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize components
fetcher = StockDataFetcher()
predictor = MLPredictor()
advisor = InvestmentAdvisor()

# Initialize FinBERT (if available)
try:
    from finbert_integration import FinBERTStockAnalyzer
    finbert_analyzer = FinBERTStockAnalyzer()
    FINBERT_ENABLED = True
    logger.info("FinBERT sentiment analysis enabled")
except ImportError as e:
    finbert_analyzer = None
    FINBERT_ENABLED = False
    logger.warning(f"FinBERT not available: {e}")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache for reducing API calls
cache = {}
CACHE_DURATION = 60  # seconds


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/stock/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    """
    Get live stock data
    
    Query params:
    - exchange: NSE (default) or BSE
    """
    try:
        exchange = request.args.get('exchange', 'NSE')
        
        logger.info(f"Fetching data for {symbol} on {exchange}")
        
        # Fetch live data
        current_data = fetcher.fetch_live_data(symbol, exchange)
        
        return jsonify({
            'success': True,
            'data': current_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching stock data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stock/<symbol>/historical', methods=['GET'])
def get_historical_data(symbol):
    """
    Get historical stock data
    
    Query params:
    - days: Number of days (default 90)
    - exchange: NSE (default) or BSE
    """
    try:
        days = int(request.args.get('days', 90))
        exchange = request.args.get('exchange', 'NSE')
        
        logger.info(f"Fetching {days} days of historical data for {symbol}")
        
        historical_data = fetcher.fetch_historical_data(symbol, days, exchange)
        
        # Convert DataFrame to dict for JSON serialization
        data_dict = historical_data.reset_index().to_dict('records')
        
        return jsonify({
            'success': True,
            'data': data_dict
        })
        
    except Exception as e:
        logger.error(f"Error fetching historical data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stock/<symbol>/indicators', methods=['GET'])
def get_technical_indicators(symbol):
    """
    Get technical indicators for a stock
    
    Query params:
    - exchange: NSE (default) or BSE
    """
    try:
        exchange = request.args.get('exchange', 'NSE')
        
        logger.info(f"Calculating technical indicators for {symbol}")
        
        # Fetch historical data
        historical_data = fetcher.fetch_historical_data(symbol, 90, exchange)
        
        # Calculate indicators
        indicators = {
            'rsi': TechnicalIndicators.calculate_rsi(historical_data['Close']),
            'macd': TechnicalIndicators.calculate_macd(historical_data['Close']),
            'bollinger_bands': TechnicalIndicators.calculate_bollinger_bands(historical_data['Close']),
            'stochastic': TechnicalIndicators.calculate_stochastic_oscillator(
                historical_data['High'],
                historical_data['Low'],
                historical_data['Close']
            )
        }
        
        return jsonify({
            'success': True,
            'indicators': indicators
        })
        
    except Exception as e:
        logger.error(f"Error calculating indicators: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stock/<symbol>/prediction', methods=['GET'])
def get_prediction(symbol):
    """
    Get ML price prediction
    
    Query params:
    - horizon: Number of days ahead (default 1)
    - exchange: NSE (default) or BSE
    """
    try:
        horizon = int(request.args.get('horizon', 1))
        exchange = request.args.get('exchange', 'NSE')
        
        logger.info(f"Generating prediction for {symbol}, horizon: {horizon} days")
        
        # Fetch historical data
        historical_data = fetcher.fetch_historical_data(symbol, 90, exchange)
        
        # Generate prediction
        prediction = predictor.predict_price(historical_data, horizon)
        
        if prediction:
            return jsonify({
                'success': True,
                'prediction': prediction
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Insufficient data for prediction'
            }), 400
            
    except Exception as e:
        logger.error(f"Error generating prediction: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stock/<symbol>/recommendation', methods=['GET'])
def get_recommendation(symbol):
    """
    Get investment recommendation
    
    Query params:
    - risk_profile: conservative, moderate (default), or aggressive
    - exchange: NSE (default) or BSE
    - include_sentiment: true/false (default true if FinBERT available)
    """
    try:
        risk_profile = request.args.get('risk_profile', 'moderate')
        exchange = request.args.get('exchange', 'NSE')
        include_sentiment = request.args.get('include_sentiment', 'true').lower() == 'true'
        
        logger.info(f"Generating recommendation for {symbol}, risk profile: {risk_profile}")
        
        # Fetch all required data
        current_data = fetcher.fetch_live_data(symbol, exchange)
        historical_data = fetcher.fetch_historical_data(symbol, 90, exchange)
        
        # Calculate indicators
        indicators = {
            'rsi': TechnicalIndicators.calculate_rsi(historical_data['Close']),
            'macd': TechnicalIndicators.calculate_macd(historical_data['Close']),
            'bollinger_bands': TechnicalIndicators.calculate_bollinger_bands(historical_data['Close'])
        }
        
        # Generate prediction
        prediction = predictor.predict_price(historical_data, horizon=1)
        
        # Get sentiment if enabled
        sentiment_data = None
        if FINBERT_ENABLED and include_sentiment and finbert_analyzer:
            try:
                logger.info("Analyzing sentiment with FinBERT...")
                sentiment_data = finbert_analyzer.analyze_stock_sentiment(
                    symbol=symbol,
                    include_news=True,
                    include_social=True,
                    days_back=7
                )
            except Exception as e:
                logger.error(f"Error in sentiment analysis: {e}")
        
        # Generate recommendation with sentiment
        recommendation = advisor.generate_recommendation(
            current_data,
            prediction,
            indicators,
            risk_profile,
            sentiment_data=sentiment_data
        )
        
        response_data = {
            'success': True,
            'recommendation': recommendation
        }
        
        # Add sentiment summary if available
        if sentiment_data:
            response_data['sentiment_summary'] = {
                'overall_sentiment': sentiment_data['overall_sentiment']['overall_sentiment'],
                'confidence': sentiment_data['overall_sentiment']['confidence'],
                'insights': sentiment_data.get('insights', [])
            }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error generating recommendation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stock/<symbol>/sentiment', methods=['GET'])
def get_sentiment(symbol):
    """
    Get FinBERT sentiment analysis
    
    Query params:
    - days: Number of days to look back (default 7)
    - include_news: true/false (default true)
    - include_social: true/false (default true)
    """
    if not FINBERT_ENABLED or not finbert_analyzer:
        return jsonify({
            'success': False,
            'error': 'FinBERT sentiment analysis not available. Install with: pip install transformers torch'
        }), 503
    
    try:
        days = int(request.args.get('days', 7))
        include_news = request.args.get('include_news', 'true').lower() == 'true'
        include_social = request.args.get('include_social', 'true').lower() == 'true'
        
        logger.info(f"Analyzing sentiment for {symbol}")
        
        # Perform sentiment analysis
        sentiment_results = finbert_analyzer.analyze_stock_sentiment(
            symbol=symbol,
            include_news=include_news,
            include_social=include_social,
            days_back=days
        )
        
        # Get trading signal from sentiment
        trading_signal = finbert_analyzer.get_sentiment_signal(sentiment_results)
        
        return jsonify({
            'success': True,
            'sentiment': sentiment_results,
            'trading_signal': trading_signal
        })
        
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stock/<symbol>/complete', methods=['GET'])
def get_complete_analysis(symbol):
    """
    Get complete analysis including data, indicators, prediction, recommendation, and sentiment
    
    Query params:
    - risk_profile: conservative, moderate (default), or aggressive
    - exchange: NSE (default) or BSE
    - include_sentiment: true/false (default true if FinBERT available)
    """
    try:
        risk_profile = request.args.get('risk_profile', 'moderate')
        exchange = request.args.get('exchange', 'NSE')
        include_sentiment = request.args.get('include_sentiment', 'true').lower() == 'true'
        
        logger.info(f"Generating complete analysis for {symbol}")
        
        # Fetch all data
        current_data = fetcher.fetch_live_data(symbol, exchange)
        historical_data = fetcher.fetch_historical_data(symbol, 90, exchange)
        
        # Calculate indicators
        indicators = {
            'rsi': TechnicalIndicators.calculate_rsi(historical_data['Close']),
            'macd': TechnicalIndicators.calculate_macd(historical_data['Close']),
            'bollinger_bands': TechnicalIndicators.calculate_bollinger_bands(historical_data['Close']),
            'stochastic': TechnicalIndicators.calculate_stochastic_oscillator(
                historical_data['High'],
                historical_data['Low'],
                historical_data['Close']
            )
        }
        
        # Generate prediction
        prediction = predictor.predict_price(historical_data, horizon=1)
        
        # Get sentiment if enabled
        sentiment_data = None
        if FINBERT_ENABLED and include_sentiment and finbert_analyzer:
            try:
                logger.info("Analyzing sentiment with FinBERT...")
                sentiment_data = finbert_analyzer.analyze_stock_sentiment(
                    symbol=symbol,
                    include_news=True,
                    include_social=True,
                    days_back=7
                )
            except Exception as e:
                logger.error(f"Error in sentiment analysis: {e}")
        
        # Generate recommendation with sentiment
        recommendation = advisor.generate_recommendation(
            current_data,
            prediction,
            indicators,
            risk_profile,
            sentiment_data=sentiment_data
        )
        
        # Prepare historical data for response
        historical_dict = historical_data.tail(30).reset_index().to_dict('records')
        
        response_data = {
            'success': True,
            'data': {
                'current': current_data,
                'historical': historical_dict,
                'indicators': indicators,
                'prediction': prediction,
                'recommendation': recommendation,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Add sentiment data if available
        if sentiment_data:
            response_data['data']['sentiment'] = {
                'overall': sentiment_data['overall_sentiment'],
                'news': sentiment_data.get('news_sentiment'),
                'social': sentiment_data.get('social_sentiment'),
                'insights': sentiment_data.get('insights', []),
                'momentum': sentiment_data.get('sentiment_momentum', {})
            }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in complete analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stocks/batch', methods=['POST'])
def get_batch_stocks():
    """
    Get data for multiple stocks in one request
    
    Request body:
    {
        "symbols": ["RELIANCE", "TCS", "INFY"],
        "exchange": "NSE"
    }
    """
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        exchange = data.get('exchange', 'NSE')
        
        if not symbols:
            return jsonify({
                'success': False,
                'error': 'No symbols provided'
            }), 400
        
        logger.info(f"Fetching batch data for {len(symbols)} stocks")
        
        results = {}
        for symbol in symbols:
            try:
                current_data = fetcher.fetch_live_data(symbol, exchange)
                results[symbol] = {
                    'success': True,
                    'data': current_data
                }
            except Exception as e:
                results[symbol] = {
                    'success': False,
                    'error': str(e)
                }
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error in batch fetch: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    """Get popular stocks for watchlist"""
    popular_stocks = [
        {'symbol': 'RELIANCE', 'name': 'Reliance Industries', 'sector': 'Energy'},
        {'symbol': 'TCS', 'name': 'Tata Consultancy Services', 'sector': 'IT'},
        {'symbol': 'HDFCBANK', 'name': 'HDFC Bank', 'sector': 'Banking'},
        {'symbol': 'INFY', 'name': 'Infosys', 'sector': 'IT'},
        {'symbol': 'ICICIBANK', 'name': 'ICICI Bank', 'sector': 'Banking'},
        {'symbol': 'HINDUNILVR', 'name': 'Hindustan Unilever', 'sector': 'FMCG'},
        {'symbol': 'ITC', 'name': 'ITC Limited', 'sector': 'FMCG'},
        {'symbol': 'SBIN', 'name': 'State Bank of India', 'sector': 'Banking'},
        {'symbol': 'BHARTIARTL', 'name': 'Bharti Airtel', 'sector': 'Telecom'},
        {'symbol': 'KOTAKBANK', 'name': 'Kotak Mahindra Bank', 'sector': 'Banking'},
    ]
    
    return jsonify({
        'success': True,
        'stocks': popular_stocks
    })


@app.route('/api/sectors', methods=['GET'])
def get_sectors():
    """Get sector-wise stock information"""
    sectors = {
        'Banking': ['HDFCBANK', 'ICICIBANK', 'SBIN', 'KOTAKBANK', 'AXISBANK'],
        'IT': ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM'],
        'Energy': ['RELIANCE', 'ONGC', 'BPCL', 'IOC', 'NTPC'],
        'FMCG': ['HINDUNILVR', 'ITC', 'NESTLEIND', 'BRITANNIA', 'DABUR'],
        'Auto': ['MARUTI', 'TATAMOTORS', 'M&M', 'BAJAJ-AUTO', 'HEROMOTOCO'],
        'Pharma': ['SUNPHARMA', 'DRREDDY', 'CIPLA', 'DIVISLAB', 'BIOCON'],
    }
    
    return jsonify({
        'success': True,
        'sectors': sectors
    })


if __name__ == '__main__':
    logger.info("Starting Stock Analytics API Server...")
    logger.info("Access the API at http://localhost:5000")
    
    # Run the server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True  # Set to False in production
    )
