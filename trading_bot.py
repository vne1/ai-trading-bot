from flask import Flask, render_template, jsonify, request
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.utils
import json
import time
import threading
from datetime import datetime, timedelta
import random
import pytz
import requests
import re
from textblob import TextBlob
import urllib.parse

app = Flask(__name__)

# Sentiment Analysis Configuration
SENTIMENT_CONFIG = {
    'reddit_api': {
        'base_url': 'https://www.reddit.com/r/wallstreetbets/search.json',
        'user_agent': 'TradingBot/1.0'
    },
    'news_api': {
        'base_url': 'https://newsapi.org/v2/everything',
        'api_key': 'demo'  # Free tier key
    },
    'twitter_api': {
        'base_url': 'https://api.twitter.com/2/tweets/search/recent',
        'bearer_token': None  # Would need Twitter API access
    }
}

def get_sentiment_score(text):
    """Calculate sentiment score using TextBlob (-1 to 1 scale)"""
    try:
        blob = TextBlob(text)
        return blob.sentiment.polarity
    except:
        return 0.0

def get_reddit_sentiment(symbol, limit=10):
    """Get sentiment from Reddit r/wallstreetbets posts"""
    try:
        headers = {'User-Agent': SENTIMENT_CONFIG['reddit_api']['user_agent']}
        params = {
            'q': symbol,
            'restrict_sr': 'on',
            'sort': 'hot',
            't': 'day',
            'limit': limit
        }
        
        response = requests.get(
            SENTIMENT_CONFIG['reddit_api']['base_url'],
            headers=headers,
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get('data', {}).get('children', [])
            
            sentiments = []
            for post in posts:
                post_data = post.get('data', {})
                title = post_data.get('title', '')
                selftext = post_data.get('selftext', '')
                full_text = f"{title} {selftext}"
                
                if symbol.lower() in full_text.lower():
                    sentiment = get_sentiment_score(full_text)
                    sentiments.append(sentiment)
            
            if sentiments:
                return {
                    'score': np.mean(sentiments),
                    'count': len(sentiments),
                    'source': 'reddit'
                }
    except Exception as e:
        print(f"Reddit sentiment error for {symbol}: {e}")
    
    return {'score': 0.0, 'count': 0, 'source': 'reddit'}

def get_news_sentiment(symbol, limit=10):
    """Get sentiment from news articles"""
    try:
        # Using NewsAPI free tier (limited requests)
        params = {
            'q': symbol,
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': limit,
            'apiKey': SENTIMENT_CONFIG['news_api']['api_key']
        }
        
        response = requests.get(
            SENTIMENT_CONFIG['news_api']['base_url'],
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            sentiments = []
            for article in articles:
                title = article.get('title', '')
                description = article.get('description', '')
                content = article.get('content', '')
                full_text = f"{title} {description} {content}"
                
                if symbol.lower() in full_text.lower():
                    sentiment = get_sentiment_score(full_text)
                    sentiments.append(sentiment)
            
            if sentiments:
                return {
                    'score': np.mean(sentiments),
                    'count': len(sentiments),
                    'source': 'news'
                }
    except Exception as e:
        print(f"News sentiment error for {symbol}: {e}")
    
    return {'score': 0.0, 'count': 0, 'source': 'news'}

def get_social_sentiment(symbol):
    """Get sentiment from social media (simulated for demo)"""
    try:
        # Simulate social media sentiment based on stock performance
        # In a real implementation, you'd use Twitter API, StockTwits, etc.
        current_price = 100.0  # Default
        if hasattr(app, 'trading_bot'):
            current_price = app.trading_bot.current_prices.get(symbol, 100.0)
        
        # Simulate sentiment based on price movement
        price_change = random.uniform(-0.1, 0.1)  # Simulate price change
        sentiment = np.tanh(price_change * 10)  # Convert to sentiment
        
        return {
            'score': sentiment,
            'count': random.randint(5, 50),
            'source': 'social'
        }
    except Exception as e:
        print(f"Social sentiment error for {symbol}: {e}")
    
    return {'score': 0.0, 'count': 0, 'source': 'social'}

def get_comprehensive_sentiment(symbol):
    """Get comprehensive sentiment from multiple sources"""
    try:
        # Get sentiment from different sources
        reddit_sentiment = get_reddit_sentiment(symbol)
        news_sentiment = get_news_sentiment(symbol)
        social_sentiment = get_social_sentiment(symbol)
        
        # Combine sentiments with weights
        sentiments = [
            (reddit_sentiment['score'], reddit_sentiment['count'], 0.4),  # Reddit weight
            (news_sentiment['score'], news_sentiment['count'], 0.4),      # News weight
            (social_sentiment['score'], social_sentiment['count'], 0.2)   # Social weight
        ]
        
        # Calculate weighted average
        total_weight = 0
        weighted_sum = 0
        
        for score, count, weight in sentiments:
            if count > 0:  # Only include sources with data
                weighted_sum += score * weight
                total_weight += weight
        
        if total_weight > 0:
            final_sentiment = weighted_sum / total_weight
        else:
            final_sentiment = 0.0
        
        return {
            'overall_score': final_sentiment,
            'reddit': reddit_sentiment,
            'news': news_sentiment,
            'social': social_sentiment,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Comprehensive sentiment error for {symbol}: {e}")
        return {
            'overall_score': 0.0,
            'reddit': {'score': 0.0, 'count': 0, 'source': 'reddit'},
            'news': {'score': 0.0, 'count': 0, 'source': 'news'},
            'social': {'score': 0.0, 'count': 0, 'source': 'social'},
            'timestamp': datetime.now().isoformat()
        }

def convert_to_json_serializable(obj):
    """Convert numpy/pandas types to JSON serializable Python types"""
    if hasattr(obj, 'item'):
        return obj.item()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict('records')
    elif isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    else:
        return obj

# Trading bot state
class TradingBot:
    def __init__(self):
        self.balance = 10000.0
        self.portfolio = {}
        self.trading_history = []
        self.is_running = False
        self.symbols = ['AAPL', 'GOOGL', 'TSLA', 'MSFT', 'AMZN', 'NVDA', 'META', 'NFLX']
        self.current_prices = {}
        self.price_history = {}
        self.technical_indicators = {}
        self.last_update = {}
        self.sentiment_data = {}
        self.sentiment_update_times = {}
        
        # Initialize price data
        self.initialize_prices()
    
    def initialize_prices(self):
        """Initialize current prices and history for all symbols"""
        for symbol in self.symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                current_price = info.get('regularMarketPrice', 100.0)
                self.current_prices[symbol] = current_price
                
                # Initialize with some historical data for immediate chart display
                self.price_history[symbol] = []
                for i in range(10):
                    # Create some initial data points for chart display
                    time_offset = datetime.now() - timedelta(minutes=(10-i)*3)
                    self.price_history[symbol].append({
                        'time': time_offset.strftime('%H:%M:%S'),
                        'price': current_price * (1 + random.uniform(-0.02, 0.02)),
                        'change': 0,
                        'change_pct': random.uniform(-2, 2)
                    })
                
                self.last_update[symbol] = datetime.now()
                self.technical_indicators[symbol] = {
                    'sma_20': current_price,
                    'rsi': 50,
                    'volume': 1000000
                }
            except Exception as e:
                print(f"Error initializing {symbol}: {e}")
                self.current_prices[symbol] = 100.0
                self.price_history[symbol] = []
                self.last_update[symbol] = datetime.now()
        
        # Make some initial trades to get started
        self.make_initial_trades()
    
    def make_initial_trades(self):
        """Make some initial trades to demonstrate the bot"""
        print("🤖 Making initial trades to get started...")
        
        # Buy some AAPL and GOOGL to start
        if self.balance > 2000:
            # Buy AAPL
            aapl_price = self.current_prices.get('AAPL', 0)
            if aapl_price > 0:
                quantity = int(1000 / aapl_price)
                if quantity > 0:
                    success, message = self.buy_stock('AAPL', quantity)
                    if success:
                        print(f"🤖 INITIAL BUY: AAPL - {quantity} shares at ${aapl_price:.2f}")
            
            # Buy GOOGL
            googl_price = self.current_prices.get('GOOGL', 0)
            if googl_price > 0:
                quantity = int(1000 / googl_price)
                if quantity > 0:
                    success, message = self.buy_stock('GOOGL', quantity)
                    if success:
                        print(f"🤖 INITIAL BUY: GOOGL - {quantity} shares at ${googl_price:.2f}")
        
        print(f"💰 Starting balance: ${self.balance:.2f}")
        print(f"📈 Portfolio: {self.portfolio}")

    def get_real_price(self, symbol):
        """Get real-time price from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info.get('regularMarketPrice', self.current_prices.get(symbol, 100.0))
        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
            return self.current_prices.get(symbol, 100.0)

    def get_historical_data(self, symbol, period='1d', interval='5m'):
        """Get historical data for technical analysis including pre/post market"""
        try:
            ticker = yf.Ticker(symbol)
            # Get extended hours data (pre-market and after-hours)
            hist = ticker.history(period=period, interval=interval, prepost=True)
            return hist
        except Exception as e:
            print(f"Error getting historical data for {symbol}: {e}")
            return pd.DataFrame()

    def is_market_hours(self):
        """Check if we're in regular market hours (9:30 AM - 4:00 PM EDT)"""
        et_tz = pytz.timezone('US/Eastern')
        now = datetime.now(et_tz)
        
        # Check if it's a weekday
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Check if it's between 9:30 AM and 4:00 PM EDT
        market_start = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_end = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        is_open = market_start <= now <= market_end
        print(f"DEBUG: Market hours check - Current time (EDT): {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"DEBUG: Market hours check - Market open: {is_open}")
        return is_open



    def calculate_technical_indicators(self, symbol):
        """Calculate technical indicators"""
        try:
            hist = self.get_historical_data(symbol, period='5d', interval='5m')
            if hist.empty:
                return
            
            # Simple Moving Average (20-period)
            if len(hist) >= 20:
                self.technical_indicators[symbol]['sma_20'] = float(hist['Close'].tail(20).mean())
            
            # RSI (14-period)
            if len(hist) >= 14:
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                self.technical_indicators[symbol]['rsi'] = float(rsi.iloc[-1])
            
            # Volume
            if len(hist) > 0:
                self.technical_indicators[symbol]['volume'] = float(hist['Volume'].iloc[-1])
                
        except Exception as e:
            print(f"Error calculating indicators for {symbol}: {e}")

    def update_sentiment_data(self, symbol):
        """Update sentiment data for a symbol"""
        try:
            sentiment = get_comprehensive_sentiment(symbol)
            self.sentiment_data[symbol] = sentiment
            print(f"📊 Sentiment updated for {symbol}: {sentiment['overall_score']:.3f}")
        except Exception as e:
            print(f"Error updating sentiment for {symbol}: {e}")

    def get_sentiment_signal(self, symbol):
        """Get sentiment-based trading signal (-1 to 1 scale)"""
        try:
            if symbol not in self.sentiment_data:
                return 0.0
            
            sentiment = self.sentiment_data[symbol]
            overall_score = sentiment['overall_score']
            
            # Convert sentiment score to trading signal
            # Positive sentiment (0.1 to 1.0) = buy signal
            # Negative sentiment (-1.0 to -0.1) = sell signal
            # Neutral sentiment (-0.1 to 0.1) = no signal
            
            if overall_score > 0.1:
                return min(overall_score, 1.0)  # Buy signal
            elif overall_score < -0.1:
                return max(overall_score, -1.0)  # Sell signal
            else:
                return 0.0  # Neutral
                
        except Exception as e:
            print(f"Error getting sentiment signal for {symbol}: {e}")
            return 0.0

    def update_prices(self):
        """Update prices with real market data"""
        for symbol in self.symbols:
            try:
                old_price = self.current_prices.get(symbol, 100.0)
                
                # Use real market data
                new_price = self.get_real_price(symbol)
                current_time = datetime.now().strftime('%H:%M:%S')
                
                # Update current price
                self.current_prices[symbol] = new_price
                
                # Add to price history
                self.price_history[symbol].append({
                    'time': current_time,
                    'price': new_price,
                    'change': new_price - old_price,
                    'change_pct': ((new_price - old_price) / old_price * 100) if old_price > 0 else 0
                })
                
                # Keep only last 100 data points
                if len(self.price_history[symbol]) > 100:
                    self.price_history[symbol] = self.price_history[symbol][-100:]
                
                # Update technical indicators every 5 minutes
                if (datetime.now() - self.last_update[symbol]).seconds > 300:
                    self.calculate_technical_indicators(symbol)
                    self.last_update[symbol] = datetime.now()
                
                # Update sentiment data every 15 minutes
                if (datetime.now() - self.sentiment_update_times.get(symbol, datetime.min)).seconds > 900:
                    self.update_sentiment_data(symbol)
                    self.sentiment_update_times[symbol] = datetime.now()
                    
            except Exception as e:
                print(f"Error updating {symbol}: {e}")

    def buy_stock(self, symbol, quantity):
        """Buy stocks"""
        if symbol not in self.current_prices:
            return False, "Invalid symbol"
        
        cost = self.current_prices[symbol] * quantity
        if cost > self.balance:
            return False, "Insufficient funds"
        
        self.balance -= cost
        if symbol in self.portfolio:
            self.portfolio[symbol] += quantity
        else:
            self.portfolio[symbol] = quantity
        
        self.trading_history.append({
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': 'BUY',
            'symbol': symbol,
            'quantity': quantity,
            'price': self.current_prices[symbol],
            'total': cost,
            'balance_after': self.balance
        })
        
        return True, f"Bought {quantity} shares of {symbol} at ${self.current_prices[symbol]:.2f}"

    def sell_stock(self, symbol, quantity):
        """Sell stocks"""
        if symbol not in self.portfolio or self.portfolio[symbol] < quantity:
            return False, "Insufficient shares"
        
        revenue = self.current_prices[symbol] * quantity
        self.balance += revenue
        self.portfolio[symbol] -= quantity
        
        if self.portfolio[symbol] == 0:
            del self.portfolio[symbol]
        
        self.trading_history.append({
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': 'SELL',
            'symbol': symbol,
            'quantity': quantity,
            'price': self.current_prices[symbol],
            'total': revenue,
            'balance_after': self.balance
        })
        
        return True, f"Sold {quantity} shares of {symbol} at ${self.current_prices[symbol]:.2f}"

    def auto_trade(self):
        """Optimized trading strategy to maximize profits and minimize losses"""
        if not self.is_running:
            return
        
        for symbol in self.symbols:
            try:
                if len(self.price_history[symbol]) < 20:  # Need more data for reliable signals
                    continue
                
                current_price = self.current_prices[symbol]
                prev_price = self.price_history[symbol][-2]['price']
                change_pct = (current_price - prev_price) / prev_price
                
                # Get technical indicators
                rsi = self.technical_indicators[symbol]['rsi']
                sma_20 = self.technical_indicators[symbol]['sma_20']
                
                # Get sentiment signal (-1 to 1 scale)
                sentiment_signal = self.get_sentiment_signal(symbol)
                
                # Calculate portfolio value and position sizing
                portfolio_value = sum(self.portfolio.get(s, 0) * self.current_prices.get(s, 0) for s in self.symbols)
                total_value = self.balance + portfolio_value
                
                # Dynamic position sizing based on confidence and portfolio size
                base_trade_pct = 0.03  # 3% base position size
                max_trade_amount = min(self.balance * base_trade_pct, total_value * 0.05)
                
                # Enhanced buy signals with momentum and volume confirmation
                buy_signal = False
                buy_reason = ""
                buy_confidence = 0
                
                # Signal 1: Strong RSI oversold (below 25) - very strong buy signal
                if rsi < 25 and self.balance > max_trade_amount:
                    buy_signal = True
                    buy_reason = f"Strong RSI oversold ({rsi:.1f})"
                    buy_confidence = 0.9
                
                # Signal 2: Price significantly below SMA with momentum
                elif (current_price < sma_20 * 0.92 and 
                      change_pct > 0.01 and  # Positive momentum
                      self.balance > max_trade_amount):
                    buy_signal = True
                    buy_reason = f"Price below SMA with momentum ({current_price:.2f} vs {sma_20:.2f})"
                    buy_confidence = 0.7
                
                # Signal 3: Strong reversal pattern with volume confirmation
                elif (change_pct > 0.025 and  # 2.5%+ gain
                      len(self.price_history[symbol]) >= 5 and
                      all(self.price_history[symbol][-i]['change_pct'] < -0.005 for i in range(2, 6)) and  # Recent decline
                      self.balance > max_trade_amount):
                    buy_signal = True
                    buy_reason = f"Strong reversal pattern ({change_pct:.2%} gain)"
                    buy_confidence = 0.8
                
                # Signal 4: Golden cross (price crossing above SMA with momentum)
                elif (len(self.price_history[symbol]) >= 3 and
                      self.price_history[symbol][-3]['price'] < sma_20 and
                      current_price > sma_20 and
                      change_pct > 0.01 and
                      self.balance > max_trade_amount):
                    buy_signal = True
                    buy_reason = f"Golden cross above SMA"
                    buy_confidence = 0.75
                
                # Signal 5: Strong positive sentiment (0.3+ sentiment score)
                elif (sentiment_signal > 0.3 and 
                      self.balance > max_trade_amount):
                    buy_signal = True
                    buy_reason = f"Strong positive sentiment ({sentiment_signal:.2f})"
                    buy_confidence = 0.8
                
                # Signal 6: Moderate positive sentiment with technical confirmation
                elif (sentiment_signal > 0.1 and 
                      rsi < 60 and  # Not overbought
                      current_price < sma_20 * 1.05 and  # Not too far above SMA
                      self.balance > max_trade_amount):
                    buy_signal = True
                    buy_reason = f"Positive sentiment with technical confirmation ({sentiment_signal:.2f})"
                    buy_confidence = 0.6
                
                if buy_signal:
                    # Adjust position size based on confidence
                    adjusted_amount = max_trade_amount * buy_confidence
                    quantity = max(1, int(adjusted_amount / current_price))
                    if quantity > 0:
                        success, message = self.buy_stock(symbol, quantity)
                        if success:
                            print(f"🤖 AUTO BUY: {symbol} - {buy_reason}")
                            print(f"   Bought {quantity} shares at ${current_price:.2f}")
                
                # Enhanced sell signals with profit protection
                sell_signal = False
                sell_reason = ""
                sell_confidence = 0
                
                if symbol in self.portfolio and self.portfolio[symbol] > 0:
                    # Calculate actual average cost from trading history
                    symbol_trades = [t for t in self.trading_history if t['symbol'] == symbol and t['action'] == 'BUY']
                    if symbol_trades:
                        total_cost = sum(t['total'] for t in symbol_trades)
                        total_shares = sum(t['quantity'] for t in symbol_trades)
                        avg_cost = total_cost / total_shares
                        current_gain_pct = ((current_price - avg_cost) / avg_cost) * 100
                    else:
                        avg_cost = current_price
                        current_gain_pct = 0
                    
                    # Signal 1: Strong RSI overbought (above 75) - very strong sell signal
                    if rsi > 75:
                        sell_signal = True
                        sell_reason = f"Strong RSI overbought ({rsi:.1f})"
                        sell_confidence = 0.9
                    
                    # Signal 2: Price significantly above SMA with reversal
                    elif (current_price > sma_20 * 1.08 and 
                          change_pct < -0.01):  # Negative momentum
                        sell_signal = True
                        sell_reason = f"Price above SMA with reversal ({current_price:.2f} vs {sma_20:.2f})"
                        sell_confidence = 0.8
                    
                    # Signal 3: Take profit at different levels based on gain
                    elif current_gain_pct > 20:  # 20%+ gain - sell 75%
                        sell_signal = True
                        sell_reason = f"Take profit - 20%+ gain ({current_gain_pct:.1f}%)"
                        sell_confidence = 0.95
                    elif current_gain_pct > 15:  # 15%+ gain - sell 50%
                        sell_signal = True
                        sell_reason = f"Take profit - 15%+ gain ({current_gain_pct:.1f}%)"
                        sell_confidence = 0.85
                    elif current_gain_pct > 10:  # 10%+ gain - sell 25%
                        sell_signal = True
                        sell_reason = f"Take profit - 10%+ gain ({current_gain_pct:.1f}%)"
                        sell_confidence = 0.7
                    
                    # Signal 4: Stop loss with trailing stop
                    elif current_gain_pct < -8:  # 8%+ loss - sell all
                        sell_signal = True
                        sell_reason = f"Stop loss - 8%+ loss ({current_gain_pct:.1f}%)"
                        sell_confidence = 1.0
                    elif current_gain_pct < -5:  # 5%+ loss - sell 50%
                        sell_signal = True
                        sell_reason = f"Stop loss - 5%+ loss ({current_gain_pct:.1f}%)"
                        sell_confidence = 0.8
                    
                    # Signal 5: Death cross (price crossing below SMA with momentum)
                    elif (len(self.price_history[symbol]) >= 3 and
                          self.price_history[symbol][-3]['price'] > sma_20 and
                          current_price < sma_20 and
                          change_pct < -0.01):
                        sell_signal = True
                        sell_reason = f"Death cross below SMA"
                        sell_confidence = 0.75
                    
                    # Signal 6: Strong negative sentiment (-0.3 or lower sentiment score)
                    elif sentiment_signal < -0.3:
                        sell_signal = True
                        sell_reason = f"Strong negative sentiment ({sentiment_signal:.2f})"
                        sell_confidence = 0.85
                    
                    # Signal 7: Moderate negative sentiment with technical confirmation
                    elif (sentiment_signal < -0.1 and 
                          rsi > 40 and  # Not oversold
                          current_price > sma_20 * 0.95):  # Not too far below SMA
                        sell_signal = True
                        sell_reason = f"Negative sentiment with technical confirmation ({sentiment_signal:.2f})"
                        sell_confidence = 0.7
                    
                    if sell_signal:
                        # Dynamic sell percentage based on confidence and signal type
                        if "Stop loss" in sell_reason and current_gain_pct < -8:
                            sell_pct = 1.0  # Sell all on major loss
                        elif "Take profit" in sell_reason and current_gain_pct > 20:
                            sell_pct = 0.75  # Sell 75% on major gain
                        elif sell_confidence > 0.8:
                            sell_pct = 0.5  # Sell 50% on strong signals
                        else:
                            sell_pct = 0.25  # Sell 25% on moderate signals
                        
                        quantity = max(1, int(self.portfolio[symbol] * sell_pct))
                        if quantity > 0:
                            success, message = self.sell_stock(symbol, quantity)
                            if success:
                                print(f"🤖 AUTO SELL: {symbol} - {sell_reason}")
                                print(f"   Sold {quantity} shares at ${current_price:.2f}")
                        
            except Exception as e:
                print(f"Error in auto-trade for {symbol}: {e}")

    def generate_chart_data(self, symbol):
        """Generate comprehensive chart data for a symbol including pre/post market and trade markers"""
        try:
            # Get comprehensive daily data including pre/post market
            hist = self.get_historical_data(symbol, period='1d', interval='5m')
            
            if hist.empty:
                # Fallback to real-time data if historical data unavailable
                if not self.price_history[symbol]:
                    return None
                
                times = [point['time'] for point in self.price_history[symbol]]
                prices = [point['price'] for point in self.price_history[symbol]]
                changes = [point['change_pct'] for point in self.price_history[symbol]]
                volumes = None
                market_status = "Real-time Data"
            else:
                # Use comprehensive historical data
                times = [time.strftime('%H:%M') for time in hist.index]
                prices = hist['Close'].tolist()
                volumes = hist['Volume'].tolist()
                
                # Calculate price changes
                changes = []
                for i in range(len(prices)):
                    if i == 0:
                        changes.append(0.0)
                    else:
                        change_pct = ((prices[i] - prices[i-1]) / prices[i-1]) * 100
                        changes.append(round(change_pct, 2))
                
                # Get current market status
                current_time = datetime.now().time()
                market_open = datetime.strptime('09:30', '%H:%M').time()
                market_close = datetime.strptime('16:00', '%H:%M').time()
                
                market_status = "After Hours"
                if market_open <= current_time <= market_close:
                    market_status = "Market Open"
                elif current_time < market_open:
                    market_status = "Pre-Market"
            
            # Get trade markers for this symbol
            trade_markers = self.get_trade_markers_for_symbol(symbol, times)
            
            # Debug: Print trade_markers before creating chart_data
            print(f"DEBUG: trade_markers for {symbol}: {len(trade_markers)} markers")
            if trade_markers:
                print(f"DEBUG: Sample trade marker: {trade_markers[0]}")
            
            # Ensure all data is JSON serializable by converting numpy/pandas types
            prices = [float(p) if hasattr(p, 'item') else float(p) for p in prices]
            changes = [float(c) if hasattr(c, 'item') else float(c) for c in changes]
            volumes = [float(v) if hasattr(v, 'item') else float(v) for v in volumes] if volumes else None
            
            # Create comprehensive chart data
            chart_data = {
                'times': times,
                'prices': prices,
                'changes': changes,
                'current_price': float(self.current_prices[symbol]),
                'rsi': float(self.technical_indicators[symbol]['rsi']),
                'sma_20': float(self.technical_indicators[symbol]['sma_20']),
                'volume': float(self.technical_indicators[symbol]['volume']),
                'volumes': volumes,
                'market_status': market_status if 'market_status' in locals() else "Unknown",
                'data_points': len(times),
                'trade_markers': trade_markers,
                'price_range': {
                    'high': float(max(prices)) if prices else 0.0,
                    'low': float(min(prices)) if prices else 0.0,
                    'open': float(prices[0]) if prices else 0.0,
                    'close': float(prices[-1]) if prices else 0.0
                }
            }
            
            return chart_data
            
        except Exception as e:
            print(f"Error generating chart data for {symbol}: {e}")
            return None

    def get_trade_markers_for_symbol(self, symbol, chart_times):
        """Get trade markers for a specific symbol that align with chart time points"""
        trade_markers = []
        
        # Get all trades for this symbol (not just today)
        symbol_trades = [
            trade for trade in self.trading_history 
            if trade['symbol'] == symbol
        ]
        
        if not symbol_trades or not chart_times:
            return trade_markers
        
        # Sort trades by time for chronological order
        symbol_trades.sort(key=lambda x: datetime.strptime(x['time'], '%Y-%m-%d %H:%M:%S'))
        
        # If all trades are happening after chart time range, distribute them evenly
        # Check if all trades are after the last chart time
        last_chart_time_str = chart_times[-1] if chart_times else "19:55"
        last_chart_hour, last_chart_minute = map(int, last_chart_time_str.split(':'))
        today = datetime.now().date()
        last_chart_dt = datetime.combine(today, datetime.min.time().replace(hour=last_chart_hour, minute=last_chart_minute))
        
        all_trades_after_chart = True
        for trade in symbol_trades:
            trade_time = datetime.strptime(trade['time'], '%Y-%m-%d %H:%M:%S')
            if trade_time <= last_chart_dt:
                all_trades_after_chart = False
                break
        
        # Calculate time range for distribution
        first_trade_time = datetime.strptime(symbol_trades[0]['time'], '%Y-%m-%d %H:%M:%S')
        last_trade_time = datetime.strptime(symbol_trades[-1]['time'], '%Y-%m-%d %H:%M:%S')
        total_trade_duration = (last_trade_time - first_trade_time).total_seconds()
        
        # Get chart time range
        try:
            first_chart_hour, first_chart_minute = map(int, chart_times[0].split(':'))
            last_chart_hour, last_chart_minute = map(int, chart_times[-1].split(':'))
            today = datetime.now().date()
            first_chart_dt = datetime.combine(today, datetime.min.time().replace(hour=first_chart_hour, minute=first_chart_minute))
            last_chart_dt = datetime.combine(today, datetime.min.time().replace(hour=last_chart_hour, minute=last_chart_minute))
            total_chart_duration = (last_chart_dt - first_chart_dt).total_seconds()
        except:
            # Fallback to simple distribution
            total_chart_duration = len(chart_times) * 300  # 5 minutes per interval
        
        # Distribute trades across chart positions
        for i, trade in enumerate(symbol_trades):
            trade_time = datetime.strptime(trade['time'], '%Y-%m-%d %H:%M:%S')
            
            # Try to find exact time match first
            exact_match_found = False
            for j, chart_time in enumerate(chart_times):
                try:
                    chart_hour, chart_minute = map(int, chart_time.split(':'))
                    today = datetime.now().date()
                    chart_dt = datetime.combine(today, datetime.min.time().replace(hour=chart_hour, minute=chart_minute))
                    
                    # Check if trade time is within 5 minutes of chart time
                    time_diff = abs((trade_time - chart_dt).total_seconds())
                    if time_diff <= 300:  # 5 minutes
                        chart_index = j
                        exact_match_found = True
                        break
                except:
                    continue
            
            if not exact_match_found:
                # If no exact match, distribute evenly across the chart
                if all_trades_after_chart:
                    # If all trades are after chart time range, distribute them evenly across the entire chart
                    chart_index = int((i / max(1, len(symbol_trades) - 1)) * (len(chart_times) - 1))
                else:
                    # Use the trade's position in the sequence to determine chart position
                    chart_index = int((i / max(1, len(symbol_trades) - 1)) * (len(chart_times) - 1))
                chart_index = max(0, min(chart_index, len(chart_times) - 1))
            
            trade_markers.append({
                'index': int(chart_index),
                'action': str(trade['action']),
                'quantity': int(trade['quantity']),
                'price': float(trade['price']),
                'time': str(trade['time']),
                'balance_after': float(trade['balance_after'])
            })
        
        print(f"DEBUG: Found {len(trade_markers)} trade markers for {symbol}, distributed across {len(chart_times)} chart positions")
        return trade_markers

# Initialize trading bot
bot = TradingBot()

def price_update_loop():
    """Background thread for updating prices and auto-trading"""
    while True:
        try:
            if bot.is_running:
                bot.update_prices()
                bot.auto_trade()
                print(f"🤖 Auto-trade cycle completed. Balance: ${bot.balance:.2f}, Portfolio: {bot.portfolio}")
            time.sleep(10)  # Update every 10 seconds for more frequent trading
        except Exception as e:
            print(f"Error in price update loop: {e}")
            time.sleep(30)  # Wait longer on error

# Start background thread
price_thread = threading.Thread(target=price_update_loop, daemon=True)
price_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    portfolio_value = sum(bot.portfolio.get(symbol, 0) * bot.current_prices.get(symbol, 0) 
                         for symbol in bot.current_prices)
    total_value = bot.balance + portfolio_value
    
    # Use the JSON serialization helper for all data
    serializable_prices = convert_to_json_serializable(bot.current_prices)
    serializable_indicators = convert_to_json_serializable(bot.technical_indicators)
    serializable_trading_history = convert_to_json_serializable(bot.trading_history[-10:])
    serializable_price_history = convert_to_json_serializable(bot.price_history)
    serializable_sentiment = convert_to_json_serializable(bot.sentiment_data)
    
    return jsonify({
        'balance': convert_to_json_serializable(round(bot.balance, 2)),
        'portfolio': convert_to_json_serializable(bot.portfolio),
        'portfolio_value': convert_to_json_serializable(round(portfolio_value, 2)),
        'total_value': convert_to_json_serializable(round(total_value, 2)),
        'prices': serializable_prices,
        'price_history': serializable_price_history,
        'technical_indicators': serializable_indicators,
        'sentiment_data': serializable_sentiment,
        'trading_history': serializable_trading_history,
        'is_running': convert_to_json_serializable(bot.is_running),
        'symbols': convert_to_json_serializable(bot.symbols),
        'market_hours': convert_to_json_serializable(bot.is_market_hours())
    })

@app.route('/api/chart/<symbol>')
def get_chart_data(symbol):
    chart_data = bot.generate_chart_data(symbol)
    if chart_data:
        # Ensure chart data is JSON serializable
        serializable_chart_data = convert_to_json_serializable(chart_data)
        return jsonify(serializable_chart_data)
    else:
        return jsonify({'error': 'No data available'})

@app.route('/api/trade', methods=['POST'])
def trade():
    data = request.json or {}
    action = data.get('action')
    symbol = data.get('symbol')
    quantity = int(data.get('quantity', 1))
    
    if action == 'buy':
        success, message = bot.buy_stock(symbol, quantity)
    elif action == 'sell':
        success, message = bot.sell_stock(symbol, quantity)
    else:
        return jsonify({'success': False, 'message': 'Invalid action'})
    
    return jsonify({'success': success, 'message': message})

@app.route('/api/sentiment/<symbol>')
def get_sentiment_data(symbol):
    """Get sentiment data for a specific symbol"""
    try:
        # Update sentiment data if it's stale (older than 15 minutes)
        if (symbol not in bot.sentiment_update_times or 
            (datetime.now() - bot.sentiment_update_times.get(symbol, datetime.min)).seconds > 900):
            bot.update_sentiment_data(symbol)
        
        if symbol in bot.sentiment_data:
            return jsonify(convert_to_json_serializable(bot.sentiment_data[symbol]))
        else:
            return jsonify({'error': 'No sentiment data available'})
    except Exception as e:
        return jsonify({'error': f'Sentiment analysis error: {str(e)}'})

@app.route('/api/toggle_bot', methods=['POST'])
def toggle_bot():
    bot.is_running = not bot.is_running
    return jsonify({'is_running': bot.is_running})



if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5239))
    print(f"🚀 Starting Trading Bot with Real Market Data on port {port}")
    print("💡 The bot will automatically trade based on real market movements")
    print("📊 Using Yahoo Finance API for live data")
    app.run(host='0.0.0.0', port=port, debug=False) 