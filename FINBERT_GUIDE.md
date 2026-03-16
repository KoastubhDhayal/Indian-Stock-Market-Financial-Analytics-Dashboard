# FinBERT Integration Guide

## Overview

FinBERT is a pre-trained NLP model specifically fine-tuned for financial sentiment analysis. It's based on BERT and trained on financial communication texts. This integration adds powerful sentiment analysis capabilities to the stock analytics dashboard.

## What is FinBERT?

FinBERT (Financial BERT) is a domain-specific language model that:
- Understands financial terminology and context
- Classifies text into: **Positive**, **Negative**, or **Neutral** sentiment
- Provides confidence scores for predictions
- Outperforms general-purpose sentiment models on financial texts

**Published by**: ProsusAI
**Based on**: BERT (Bidirectional Encoder Representations from Transformers)
**Training Data**: Financial news, earnings calls, analyst reports

## Installation

### Step 1: Install Dependencies

```bash
# Install PyTorch (CPU version)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Or for GPU support (CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install Transformers
pip install transformers

# Install additional dependencies
pip install sentencepiece accelerate
```

### Step 2: Verify Installation

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load FinBERT
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

print("✓ FinBERT loaded successfully!")
```

## Features Added to Dashboard

### 1. News Sentiment Analysis
- Fetches recent news articles about stocks
- Analyzes sentiment of headlines and content
- Aggregates sentiment across multiple sources
- Example: "Company reports strong Q4 earnings" → **Positive (92% confidence)**

### 2. Social Media Sentiment
- Analyzes tweets, Reddit posts, StockTwits mentions
- Real-time sentiment tracking
- Identifies trending opinions
- Example: "Just bought more $RELIANCE! 🚀" → **Positive (85% confidence)**

### 3. Sentiment-Based Trading Signals
- Converts sentiment into actionable recommendations
- Combines with technical analysis
- Risk-adjusted position sizing based on sentiment confidence
- Momentum tracking (improving/deteriorating sentiment)

### 4. Enhanced Investment Recommendations
- Original scoring: Technical (30%) + ML Prediction (35%) + Momentum (20%) + Risk (15%)
- **With FinBERT**: Technical (25%) + ML (30%) + Momentum (15%) + Risk (10%) + **Sentiment (20%)**

## How It Works

### Architecture

```
User Query → API Server → FinBERT Analyzer
                              ↓
                    News Aggregator → Fetch Articles
                    Social Analyzer → Fetch Posts
                              ↓
                    Batch Analysis (FinBERT Model)
                              ↓
                    Sentiment Aggregation
                              ↓
                    Trading Signal Generation
                              ↓
            Investment Advisor (with sentiment)
                              ↓
            Enhanced Recommendation → User
```

### Sentiment Scoring

```python
# Example sentiment analysis result
{
    'sentiment': 'positive',
    'scores': {
        'positive': 0.78,    # 78% positive
        'negative': 0.09,    # 9% negative
        'neutral': 0.13      # 13% neutral
    },
    'confidence': 0.78       # Most confident in 'positive'
}
```

### Aggregation Logic

When analyzing multiple texts (e.g., 10 news articles):

1. **Individual Analysis**: Each text gets sentiment + confidence
2. **Weighted Average**: Combine scores weighted by confidence
3. **Distribution**: Calculate % positive/negative/neutral
4. **Momentum**: Compare recent vs. older sentiment
5. **Overall Signal**: Aggregate into single recommendation

## API Usage

### Get Sentiment Analysis

```bash
# Basic sentiment analysis
curl "http://localhost:5000/api/stock/RELIANCE/sentiment"

# With custom parameters
curl "http://localhost:5000/api/stock/RELIANCE/sentiment?days=14&include_news=true&include_social=true"
```

**Response:**
```json
{
  "success": true,
  "sentiment": {
    "symbol": "RELIANCE",
    "overall_sentiment": {
      "overall_sentiment": "positive",
      "sentiment_score": 0.45,
      "confidence": 0.76,
      "distribution_percentage": {
        "positive": 65.0,
        "negative": 15.0,
        "neutral": 20.0
      }
    },
    "news_sentiment": {
      "overall_sentiment": "positive",
      "confidence": 0.81,
      "articles_analyzed": 15
    },
    "social_sentiment": {
      "overall_sentiment": "neutral",
      "confidence": 0.68,
      "posts_analyzed": 50
    },
    "insights": [
      "Strong positive sentiment with 76% confidence",
      "Alignment: Both news and social media show positive sentiment",
      "Sentiment improving over time"
    ]
  },
  "trading_signal": {
    "action": "BUY",
    "strength": 7.8,
    "reasoning": [
      "Strong positive sentiment across multiple sources",
      "Sentiment improving over time"
    ]
  }
}
```

### Get Recommendation with Sentiment

```bash
# Include sentiment in recommendation (default)
curl "http://localhost:5000/api/stock/RELIANCE/recommendation?include_sentiment=true"

# Exclude sentiment
curl "http://localhost:5000/api/stock/RELIANCE/recommendation?include_sentiment=false"
```

### Complete Analysis with Sentiment

```bash
curl "http://localhost:5000/api/stock/RELIANCE/complete"
```

## Python Usage Examples

### Basic Sentiment Analysis

```python
from finbert_integration import FinBERTStockAnalyzer

# Initialize
analyzer = FinBERTStockAnalyzer()

# Analyze single stock
results = analyzer.analyze_stock_sentiment(
    symbol="RELIANCE",
    include_news=True,
    include_social=True,
    days_back=7
)

print(f"Overall Sentiment: {results['overall_sentiment']['overall_sentiment']}")
print(f"Confidence: {results['overall_sentiment']['confidence']:.2%}")
print(f"\nInsights:")
for insight in results['insights']:
    print(f"  • {insight}")
```

### Get Trading Signal

```python
# Get sentiment-based trading signal
signal = analyzer.get_sentiment_signal(results)

print(f"Action: {signal['action']}")
print(f"Strength: {signal['strength']:.1f}/10")
print(f"\nReasoning:")
for reason in signal['reasoning']:
    print(f"  • {reason}")
```

### Batch Analysis

```python
from finbert_integration import FinBERTAnalyzer

finbert = FinBERTAnalyzer()

# Analyze multiple texts
texts = [
    "Company reports record profits, stock soars",
    "CEO resigns amid scandal, investors concerned",
    "Neutral outlook for the sector this quarter"
]

results = finbert.batch_analyze(texts)

for i, result in enumerate(results):
    print(f"{i+1}. {result['sentiment'].upper()} ({result['confidence']:.0%})")
```

### Custom News Integration

```python
from finbert_integration import NewsAggregator, FinBERTAnalyzer

# Get your own News API key from https://newsapi.org
NEWS_API_KEY = "your_api_key_here"

aggregator = NewsAggregator()
finbert = FinBERTAnalyzer()

# Fetch real news
articles = aggregator.fetch_news("RELIANCE", days=7, api_key=NEWS_API_KEY)

# Extract text
texts = aggregator.extract_text_for_analysis(articles)

# Analyze sentiment
sentiments = finbert.batch_analyze(texts)
aggregate = finbert.aggregate_sentiment(sentiments)

print(f"News Sentiment: {aggregate['overall_sentiment']}")
```

## Data Sources

### News APIs (Recommended)

1. **NewsAPI** (https://newsapi.org)
   - Free tier: 100 requests/day
   - Good coverage of financial news
   - Easy integration

2. **GNews** (https://gnews.io)
   - Free tier: 100 requests/day
   - Global news coverage
   - Clean JSON API

3. **Economic Times RSS**
   - Free
   - India-focused financial news
   - No API key required

4. **MoneyControl**
   - Free web scraping (respect robots.txt)
   - Excellent for Indian stocks
   - Requires parsing

### Social Media APIs

1. **Twitter API v2**
   - Free tier: 500k tweets/month
   - Real-time sentiment
   - Requires developer account

2. **Reddit API (PRAW)**
   - Free
   - Rich discussions
   - Good for long-form analysis

3. **StockTwits**
   - Free
   - Finance-specific
   - Good for retail sentiment

## Performance Optimization

### 1. Batch Processing

```python
# Instead of analyzing one by one
for text in texts:
    result = finbert.analyze_sentiment(text)  # Slow

# Use batch analysis
results = finbert.batch_analyze(texts, batch_size=8)  # Fast
```

### 2. GPU Acceleration

```python
import torch

# Check if GPU available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Model automatically uses GPU if available
finbert = FinBERTAnalyzer()  # Will use GPU if available
```

### 3. Model Caching

```python
# Models are cached after first load
# Subsequent initializations are fast

# First time (slow - downloads model)
analyzer1 = FinBERTStockAnalyzer()

# Second time (fast - uses cache)
analyzer2 = FinBERTStockAnalyzer()
```

### 4. Result Caching

```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0)

def get_sentiment_cached(symbol, days=7):
    cache_key = f"sentiment:{symbol}:{days}"
    cached = r.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    # Analyze
    result = analyzer.analyze_stock_sentiment(symbol, days_back=days)
    
    # Cache for 1 hour
    r.setex(cache_key, 3600, json.dumps(result))
    
    return result
```

## Model Information

### Model Specifications

- **Architecture**: BERT-base
- **Parameters**: 110M
- **Input**: Max 512 tokens
- **Output**: 3 classes (positive/negative/neutral)
- **Languages**: English
- **Domain**: Financial texts

### Performance Metrics

On financial sentiment benchmarks:
- **Accuracy**: ~94%
- **F1 Score**: 0.92
- **Precision**: 0.93
- **Recall**: 0.91

### Comparison with Alternatives

| Model | Domain | Accuracy | Speed |
|-------|--------|----------|-------|
| FinBERT | Financial | 94% | Medium |
| VADER | General | 78% | Fast |
| TextBlob | General | 72% | Very Fast |
| GPT-3.5 | General | 88% | Slow |

## Use Cases

### 1. Pre-Earnings Analysis
Analyze sentiment before earnings to gauge market expectations

### 2. News Impact Assessment
Measure immediate sentiment impact of news announcements

### 3. Social Media Monitoring
Track retail investor sentiment on Twitter/Reddit

### 4. Competitor Analysis
Compare sentiment across stocks in same sector

### 5. Risk Management
Detect negative sentiment early for risk mitigation

### 6. Long-term Sentiment Trends
Track sentiment momentum over weeks/months

## Limitations

### 1. Language
- Only supports English text
- May miss regional/local news in other languages

### 2. Context
- Limited to 512 tokens per input
- May miss context in very long articles

### 3. Sarcasm/Irony
- Can misinterpret sarcastic or ironic statements
- Example: "Great, another loss!" may be classified as positive

### 4. Market Manipulation
- Social media can contain pump-and-dump schemes
- Need to filter for credible sources

### 5. Recency
- Historical news may not reflect current situation
- Weight recent sentiment more heavily

## Best Practices

### 1. Combine Multiple Sources
Don't rely on sentiment alone - combine with:
- Technical analysis
- Fundamental analysis
- Price action
- Volume patterns

### 2. Weight by Credibility
Not all sources are equal:
- News from Reuters > Random blog
- Verified Twitter accounts > Anonymous accounts
- Recent news > Old news

### 3. Filter Noise
- Remove duplicate articles
- Filter low-quality sources
- Exclude promotional content

### 4. Time Weighting
```python
def time_weighted_sentiment(sentiments, timestamps):
    """Weight recent sentiment more heavily"""
    weights = []
    now = datetime.now()
    
    for ts in timestamps:
        age_hours = (now - ts).total_seconds() / 3600
        weight = 1 / (1 + age_hours / 24)  # Decay over 24 hours
        weights.append(weight)
    
    return weighted_average(sentiments, weights)
```

### 5. Divergence Analysis
```python
# Flag when sentiment diverges from price
if sentiment == 'positive' and price_change < -3:
    print("⚠️ Warning: Positive sentiment but price falling")
    
if sentiment == 'negative' and price_change > 3:
    print("💡 Opportunity: Negative sentiment but price rising")
```

## Troubleshooting

### Error: "No module named 'transformers'"
```bash
pip install transformers torch
```

### Error: "Model not found"
```bash
# Clear cache and re-download
rm -rf ~/.cache/huggingface/
python -c "from transformers import AutoModel; AutoModel.from_pretrained('ProsusAI/finbert')"
```

### Slow Performance
```bash
# Use GPU
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Or reduce batch size
results = finbert.batch_analyze(texts, batch_size=4)
```

### Out of Memory
```python
# Process in smaller batches
def chunked_analysis(texts, chunk_size=10):
    results = []
    for i in range(0, len(texts), chunk_size):
        chunk = texts[i:i+chunk_size]
        results.extend(finbert.batch_analyze(chunk))
    return results
```

## Advanced: Custom Fine-tuning

For even better results, fine-tune FinBERT on your specific use case:

```python
from transformers import Trainer, TrainingArguments

# Your labeled dataset
train_data = [
    {"text": "Stock soars on earnings beat", "label": "positive"},
    {"text": "Company faces regulatory issues", "label": "negative"},
    # ... more examples
]

# Fine-tune
training_args = TrainingArguments(
    output_dir="./finbert-custom",
    num_train_epochs=3,
    per_device_train_batch_size=8
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_data
)

trainer.train()
```

## Resources

- **FinBERT Paper**: https://arxiv.org/abs/1908.10063
- **HuggingFace Model**: https://huggingface.co/ProsusAI/finbert
- **Transformers Docs**: https://huggingface.co/docs/transformers
- **PyTorch Docs**: https://pytorch.org/docs/stable/index.html

## License

FinBERT is released under Apache 2.0 license and free to use for commercial purposes.

---

**Built with ❤️ for Better Financial Analysis**
