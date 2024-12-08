from textblob import TextBlob
import yfinance as yf

def analyze_news_sentiment(ticker):
    stock = yf.Ticker(ticker)
    news = stock.news
    
    sentiment_scores = []
    for article in news:
        analysis = TextBlob(article['title'])
        sentiment_scores.append(analysis.sentiment.polarity)
    
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
    return {
        'ticker': ticker,
        'sentiment_score': avg_sentiment,
        'interpretation': 'Bullish' if avg_sentiment > 0 else 'Bearish'
    }
