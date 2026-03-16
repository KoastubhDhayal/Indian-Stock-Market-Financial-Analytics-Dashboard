"""
FinBERT Integration for Financial Sentiment Analysis
Analyzes news, social media, and financial reports for stock sentiment
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from typing import List, Dict, Optional
import requests
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinBERTAnalyzer:
    """
    FinBERT-based sentiment analyzer for financial text
    Uses pre-trained FinBERT model for financial domain sentiment analysis
    """
    
    def __init__(self, model_name: str = "ProsusAI/finbert"):
        """
        Initialize FinBERT model
        
        Args:
            model_name: HuggingFace model identifier
        """
        logger.info(f"Loading FinBERT model: {model_name}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.eval()  # Set to evaluation mode
            
            # Device configuration
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.model.to(self.device)
            
            logger.info(f"FinBERT loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Error loading FinBERT: {e}")
            raise
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of financial text
        
        Args:
            text: Financial text to analyze
            
        Returns:
            Dictionary with sentiment scores and label
        """
        if not text or len(text.strip()) == 0:
            return {
                'sentiment': 'neutral',
                'scores': {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34},
                'confidence': 0.0
            }
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            ).to(self.device)
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Extract scores
            scores = predictions[0].cpu().numpy()
            
            # FinBERT outputs: [positive, negative, neutral]
            sentiment_scores = {
                'positive': float(scores[0]),
                'negative': float(scores[1]),
                'neutral': float(scores[2])
            }
            
            # Determine dominant sentiment
            sentiment_label = max(sentiment_scores, key=sentiment_scores.get)
            confidence = sentiment_scores[sentiment_label]
            
            return {
                'sentiment': sentiment_label,
                'scores': sentiment_scores,
                'confidence': confidence,
                'text_length': len(text)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                'sentiment': 'neutral',
                'scores': {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34},
                'confidence': 0.0,
                'error': str(e)
            }
    
    def batch_analyze(self, texts: List[str], batch_size: int = 8) -> List[Dict]:
        """
        Analyze multiple texts in batches for efficiency
        
        Args:
            texts: List of texts to analyze
            batch_size: Number of texts to process at once
            
        Returns:
            List of sentiment analysis results
        """
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                # Tokenize batch
                inputs = self.tokenizer(
                    batch,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512,
                    padding=True
                ).to(self.device)
                
                # Get predictions
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                
                # Process each result
                for j, scores in enumerate(predictions.cpu().numpy()):
                    sentiment_scores = {
                        'positive': float(scores[0]),
                        'negative': float(scores[1]),
                        'neutral': float(scores[2])
                    }
                    
                    sentiment_label = max(sentiment_scores, key=sentiment_scores.get)
                    
                    results.append({
                        'sentiment': sentiment_label,
                        'scores': sentiment_scores,
                        'confidence': sentiment_scores[sentiment_label],
                        'text': batch[j][:100] + '...' if len(batch[j]) > 100 else batch[j]
                    })
                    
            except Exception as e:
                logger.error(f"Error in batch analysis: {e}")
                # Add neutral sentiment for failed analyses
                for text in batch:
                    results.append({
                        'sentiment': 'neutral',
                        'scores': {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34},
                        'confidence': 0.0,
                        'error': str(e)
                    })
        
        return results
    
    def aggregate_sentiment(self, sentiments: List[Dict]) -> Dict:
        """
        Aggregate multiple sentiment analyses into overall sentiment
        
        Args:
            sentiments: List of sentiment analysis results
            
        Returns:
            Aggregated sentiment with weighted scores
        """
        if not sentiments:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'distribution': {'positive': 0, 'negative': 0, 'neutral': 0}
            }
        
        # Count sentiments
        distribution = {'positive': 0, 'negative': 0, 'neutral': 0}
        weighted_score = 0.0
        total_confidence = 0.0
        
        for sentiment in sentiments:
            label = sentiment['sentiment']
            confidence = sentiment['confidence']
            
            distribution[label] += 1
            
            # Weight: positive = +1, negative = -1, neutral = 0
            if label == 'positive':
                weighted_score += confidence
            elif label == 'negative':
                weighted_score -= confidence
            
            total_confidence += confidence
        
        # Calculate overall metrics
        num_sentiments = len(sentiments)
        avg_weighted_score = weighted_score / num_sentiments
        avg_confidence = total_confidence / num_sentiments
        
        # Determine overall sentiment
        if avg_weighted_score > 0.15:
            overall = 'positive'
        elif avg_weighted_score < -0.15:
            overall = 'negative'
        else:
            overall = 'neutral'
        
        # Calculate distribution percentages
        distribution_pct = {
            k: round(v / num_sentiments * 100, 2) 
            for k, v in distribution.items()
        }
        
        return {
            'overall_sentiment': overall,
            'sentiment_score': round(avg_weighted_score, 3),
            'confidence': round(avg_confidence, 3),
            'distribution': distribution,
            'distribution_percentage': distribution_pct,
            'total_analyzed': num_sentiments
        }


class NewsAggregator:
    """
    Aggregates news and financial content for sentiment analysis
    """
    
    def __init__(self):
        self.news_sources = {
            'newsapi': 'https://newsapi.org/v2/everything',
            'gnews': 'https://gnews.io/api/v4/search',
            'economic_times': 'https://economictimes.indiatimes.com',
            'moneycontrol': 'https://www.moneycontrol.com'
        }
    
    def fetch_news(
        self, 
        symbol: str, 
        days: int = 7,
        api_key: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch news articles related to a stock
        
        Args:
            symbol: Stock symbol
            days: Number of days to look back
            api_key: API key for news service
            
        Returns:
            List of news articles with text content
        """
        articles = []
        
        try:
            # Example using NewsAPI (requires API key)
            if api_key:
                from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                
                params = {
                    'q': f"{symbol} OR stock",
                    'from': from_date,
                    'language': 'en',
                    'sortBy': 'relevancy',
                    'apiKey': api_key
                }
                
                response = requests.get(
                    self.news_sources['newsapi'],
                    params=params,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for article in data.get('articles', [])[:20]:  # Limit to 20
                        articles.append({
                            'title': article.get('title', ''),
                            'description': article.get('description', ''),
                            'content': article.get('content', ''),
                            'source': article.get('source', {}).get('name', 'Unknown'),
                            'published_at': article.get('publishedAt', ''),
                            'url': article.get('url', '')
                        })
            
            # Fallback: Generate sample news for testing
            if not articles:
                articles = self._generate_sample_news(symbol)
            
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            articles = self._generate_sample_news(symbol)
        
        return articles
    
    def _generate_sample_news(self, symbol: str) -> List[Dict]:
        """Generate sample news for testing when API is unavailable"""
        templates = [
            f"{symbol} reports strong quarterly earnings, beats analyst estimates",
            f"{symbol} announces new expansion plans in emerging markets",
            f"Market analysts upgrade {symbol} stock rating to buy",
            f"{symbol} faces regulatory challenges in key market segment",
            f"Insider trading reported at {symbol}, stock drops",
            f"{symbol} CEO discusses future growth strategy in interview",
            f"Industry report highlights {symbol}'s competitive advantages",
            f"{symbol} invests heavily in R&D for next-gen products"
        ]
        
        return [
            {
                'title': title,
                'description': title,
                'content': title,
                'source': 'Sample News',
                'published_at': datetime.now().isoformat(),
                'url': '#'
            }
            for title in templates[:5]
        ]
    
    def extract_text_for_analysis(self, articles: List[Dict]) -> List[str]:
        """
        Extract relevant text from articles for sentiment analysis
        
        Args:
            articles: List of news articles
            
        Returns:
            List of text strings to analyze
        """
        texts = []
        
        for article in articles:
            # Combine title and description for better context
            text = f"{article.get('title', '')}. {article.get('description', '')}"
            
            # Add content if available
            content = article.get('content', '')
            if content:
                text += f" {content[:500]}"  # Limit content length
            
            if text.strip():
                texts.append(text.strip())
        
        return texts


class SocialMediaAnalyzer:
    """
    Analyze social media sentiment (Twitter, Reddit, etc.)
    """
    
    def __init__(self):
        self.platforms = ['twitter', 'reddit', 'stocktwits']
    
    def fetch_social_mentions(
        self,
        symbol: str,
        platform: str = 'twitter',
        limit: int = 100
    ) -> List[str]:
        """
        Fetch social media mentions
        
        Args:
            symbol: Stock symbol
            platform: Social media platform
            limit: Number of posts to fetch
            
        Returns:
            List of text content from social media
        """
        # In production, integrate with:
        # - Twitter API v2
        # - Reddit API (PRAW)
        # - StockTwits API
        
        # Sample social media posts for testing
        sample_posts = [
            f"Just bought more {symbol}! Great long-term play 📈",
            f"{symbol} earnings looking weak this quarter 😰",
            f"Technical analysis shows {symbol} breaking resistance!",
            f"Concerned about {symbol}'s debt levels",
            f"{symbol} innovation pipeline is impressive",
            f"Selling my {symbol} position, too much volatility",
            f"Why is everyone so bullish on {symbol}?",
            f"{symbol} dividend yield is attractive at these levels"
        ]
        
        return sample_posts[:limit]


class FinBERTStockAnalyzer:
    """
    Complete stock analysis using FinBERT sentiment + news + social media
    """
    
    def __init__(self, news_api_key: Optional[str] = None):
        """
        Initialize complete analyzer
        
        Args:
            news_api_key: API key for news services
        """
        self.finbert = FinBERTAnalyzer()
        self.news_aggregator = NewsAggregator()
        self.social_analyzer = SocialMediaAnalyzer()
        self.news_api_key = news_api_key
    
    def analyze_stock_sentiment(
        self,
        symbol: str,
        include_news: bool = True,
        include_social: bool = True,
        days_back: int = 7
    ) -> Dict:
        """
        Complete sentiment analysis for a stock
        
        Args:
            symbol: Stock symbol
            include_news: Whether to include news sentiment
            include_social: Whether to include social media sentiment
            days_back: Number of days to look back
            
        Returns:
            Comprehensive sentiment analysis report
        """
        logger.info(f"Starting comprehensive sentiment analysis for {symbol}")
        
        results = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'news_sentiment': None,
            'social_sentiment': None,
            'overall_sentiment': None
        }
        
        all_sentiments = []
        
        # Analyze news sentiment
        if include_news:
            logger.info("Fetching and analyzing news...")
            news_articles = self.news_aggregator.fetch_news(
                symbol, 
                days=days_back,
                api_key=self.news_api_key
            )
            
            if news_articles:
                news_texts = self.news_aggregator.extract_text_for_analysis(news_articles)
                news_sentiments = self.finbert.batch_analyze(news_texts)
                news_aggregate = self.finbert.aggregate_sentiment(news_sentiments)
                
                results['news_sentiment'] = {
                    **news_aggregate,
                    'articles_analyzed': len(news_articles),
                    'sample_headlines': [
                        article['title'] 
                        for article in news_articles[:3]
                    ]
                }
                
                all_sentiments.extend(news_sentiments)
        
        # Analyze social media sentiment
        if include_social:
            logger.info("Fetching and analyzing social media...")
            social_posts = self.social_analyzer.fetch_social_mentions(symbol, limit=50)
            
            if social_posts:
                social_sentiments = self.finbert.batch_analyze(social_posts)
                social_aggregate = self.finbert.aggregate_sentiment(social_sentiments)
                
                results['social_sentiment'] = {
                    **social_aggregate,
                    'posts_analyzed': len(social_posts)
                }
                
                all_sentiments.extend(social_sentiments)
        
        # Calculate overall sentiment
        if all_sentiments:
            overall = self.finbert.aggregate_sentiment(all_sentiments)
            results['overall_sentiment'] = overall
            
            # Generate insights
            results['insights'] = self._generate_insights(results)
            
            # Calculate sentiment momentum (trend over time)
            results['sentiment_momentum'] = self._calculate_momentum(all_sentiments)
        
        logger.info(f"Sentiment analysis complete for {symbol}")
        
        return results
    
    def _generate_insights(self, results: Dict) -> List[str]:
        """Generate human-readable insights from sentiment analysis"""
        insights = []
        
        overall = results.get('overall_sentiment', {})
        sentiment = overall.get('overall_sentiment', 'neutral')
        score = overall.get('sentiment_score', 0.0)
        confidence = overall.get('confidence', 0.0)
        
        # Overall sentiment insight
        if sentiment == 'positive' and confidence > 0.7:
            insights.append(f"Strong positive sentiment with {confidence*100:.0f}% confidence")
        elif sentiment == 'negative' and confidence > 0.7:
            insights.append(f"Strong negative sentiment with {confidence*100:.0f}% confidence")
        else:
            insights.append(f"Mixed or neutral sentiment across sources")
        
        # News vs Social comparison
        news_sent = results.get('news_sentiment', {}).get('overall_sentiment')
        social_sent = results.get('social_sentiment', {}).get('overall_sentiment')
        
        if news_sent and social_sent:
            if news_sent != social_sent:
                insights.append(f"Divergence: News is {news_sent}, social media is {social_sent}")
            else:
                insights.append(f"Alignment: Both news and social media show {news_sent} sentiment")
        
        # Confidence insight
        if confidence < 0.5:
            insights.append("Low confidence in sentiment - mixed signals from sources")
        
        # Score magnitude
        if abs(score) > 0.5:
            insights.append(f"Strong sentiment intensity (score: {score:.2f})")
        
        return insights
    
    def _calculate_momentum(self, sentiments: List[Dict]) -> Dict:
        """Calculate sentiment trend/momentum"""
        if len(sentiments) < 5:
            return {'trend': 'insufficient_data', 'direction': 'neutral'}
        
        # Split into first half and second half
        mid = len(sentiments) // 2
        first_half = sentiments[:mid]
        second_half = sentiments[mid:]
        
        # Calculate average sentiment scores
        def calc_avg_score(sents):
            scores = []
            for s in sents:
                if s['sentiment'] == 'positive':
                    scores.append(s['confidence'])
                elif s['sentiment'] == 'negative':
                    scores.append(-s['confidence'])
                else:
                    scores.append(0)
            return np.mean(scores) if scores else 0
        
        first_score = calc_avg_score(first_half)
        second_score = calc_avg_score(second_half)
        
        momentum = second_score - first_score
        
        if momentum > 0.1:
            trend = 'improving'
        elif momentum < -0.1:
            trend = 'deteriorating'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'momentum_score': round(momentum, 3),
            'direction': 'bullish' if momentum > 0 else 'bearish' if momentum < 0 else 'neutral'
        }
    
    def get_sentiment_signal(self, sentiment_results: Dict) -> Dict:
        """
        Convert sentiment analysis into trading signal
        
        Args:
            sentiment_results: Results from analyze_stock_sentiment
            
        Returns:
            Trading signal based on sentiment
        """
        overall = sentiment_results.get('overall_sentiment', {})
        sentiment = overall.get('overall_sentiment', 'neutral')
        score = overall.get('sentiment_score', 0.0)
        confidence = overall.get('confidence', 0.0)
        momentum = sentiment_results.get('sentiment_momentum', {})
        
        # Initialize signal
        signal = {
            'action': 'HOLD',
            'strength': 0.0,
            'reasoning': []
        }
        
        # Determine action based on sentiment and confidence
        if sentiment == 'positive' and confidence > 0.7:
            if score > 0.3:
                signal['action'] = 'BUY'
                signal['strength'] = min(confidence * score * 10, 10)
                signal['reasoning'].append("Strong positive sentiment across multiple sources")
            else:
                signal['action'] = 'HOLD'
                signal['strength'] = 5.0
                signal['reasoning'].append("Positive sentiment but moderate strength")
        
        elif sentiment == 'negative' and confidence > 0.7:
            if score < -0.3:
                signal['action'] = 'SELL'
                signal['strength'] = min(confidence * abs(score) * 10, 10)
                signal['reasoning'].append("Strong negative sentiment indicates caution")
            else:
                signal['action'] = 'HOLD'
                signal['strength'] = 5.0
                signal['reasoning'].append("Negative sentiment but moderate intensity")
        
        else:
            signal['action'] = 'HOLD'
            signal['strength'] = 5.0
            signal['reasoning'].append("Mixed or neutral sentiment - await clearer signals")
        
        # Adjust based on momentum
        if momentum.get('trend') == 'improving':
            signal['reasoning'].append("Sentiment improving over time")
            if signal['action'] == 'SELL':
                signal['action'] = 'HOLD'  # Don't sell if sentiment improving
        elif momentum.get('trend') == 'deteriorating':
            signal['reasoning'].append("Sentiment deteriorating over time")
            if signal['action'] == 'BUY':
                signal['action'] = 'HOLD'  # Don't buy if sentiment worsening
        
        return signal


# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = FinBERTStockAnalyzer()
    
    # Analyze stock sentiment
    symbol = "RELIANCE"
    
    print(f"\n{'='*60}")
    print(f"FinBERT Sentiment Analysis for {symbol}")
    print(f"{'='*60}\n")
    
    results = analyzer.analyze_stock_sentiment(
        symbol=symbol,
        include_news=True,
        include_social=True,
        days_back=7
    )
    
    # Print results
    print(f"Overall Sentiment: {results['overall_sentiment']['overall_sentiment'].upper()}")
    print(f"Sentiment Score: {results['overall_sentiment']['sentiment_score']:.3f}")
    print(f"Confidence: {results['overall_sentiment']['confidence']*100:.1f}%")
    print(f"\nDistribution:")
    for sent, pct in results['overall_sentiment']['distribution_percentage'].items():
        print(f"  {sent.capitalize()}: {pct}%")
    
    print(f"\nInsights:")
    for insight in results['insights']:
        print(f"  • {insight}")
    
    # Get trading signal
    print(f"\n{'='*60}")
    print("Trading Signal Based on Sentiment")
    print(f"{'='*60}\n")
    
    signal = analyzer.get_sentiment_signal(results)
    print(f"Action: {signal['action']}")
    print(f"Strength: {signal['strength']:.1f}/10")
    print(f"\nReasoning:")
    for reason in signal['reasoning']:
        print(f"  • {reason}")
