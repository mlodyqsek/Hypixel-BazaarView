# Hypixel Skyblock Bazaar Tracker

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=flat&logo=flask)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-4169E1?style=flat&logo=postgresql)](https://www.postgresql.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=flat&logo=javascript)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3)](https://developer.mozilla.org/en-US/docs/Web/CSS)

A real-time dashboard for tracking prices and market data in the Hypixel Skyblock bazaar. View live charts, order books, and create custom trading algorithms.

## ✨ What It Does

This application automatically collects price data from the Hypixel Skyblock bazaar every minute and displays it in an easy-to-use web interface. You can:

- **View Live Charts**: See price movements over time with different timeframes (1 minute, 5 minutes, 15 minutes, 1 hour)
- **Check Order Books**: Look at current buy and sell orders for any product
- **Use Technical Indicators**: Add moving averages, RSI, and other indicators to charts
- **Create Custom Algorithms**: Write your own JavaScript code for trading strategies
- **Search Products**: Quickly find and switch between different bazaar items

## 📊 System Overview

**View the detailed system diagram**: Import `architecture.json` into [JSON Crack](https://jsoncrack.com/) for an interactive visualization of how everything works together.

The system has three main parts:

1. **Data Collector** (`backend.py`) - Gets fresh data from Hypixel every 60 seconds
2. **Web API** (`api.py`) - Provides data to the website through simple web addresses
3. **Web Dashboard** (`frontend.html`) - Shows charts and lets you interact with the data

## 🚀 Getting Started

### What You Need
- Python 3.8 or newer
- PostgreSQL database
- Internet connection

### Installation Steps

1. **Download the code**
   ```bash
   git clone <your-repository-url>
   cd skyblock-bazaar-tracker
   ```

2. **Install required software**
   ```bash
   pip install flask flask-cors psycopg2-binary requests
   ```

3. **Set up the database**
   ```sql
   CREATE DATABASE bazaar_db;
   CREATE USER postgres WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE bazaar_db TO postgres;
   ```

### Running the Application

1. **Start data collection** (in one terminal):
   ```bash
   python backend.py
   ```

2. **Start the web server** (in another terminal):
   ```bash
   python api.py
   ```

3. **Open your browser** and go to `http://localhost:5000`

## 📈 Features

### Charts & Visualization
- Interactive candlestick charts
- Multiple timeframe options
- Volume bars
- Price overlays

### Market Data
- Real-time order books
- 24-hour price statistics
- Product search and filtering

### Technical Analysis
- Simple Moving Average (SMA)
- Exponential Moving Average (EMA)
- Bollinger Bands
- Custom algorithm support

### User Interface
- Clean, modern design
- Responsive layout
- Dark theme
- Easy navigation

## 🔧 API Reference

The application provides several web addresses (endpoints) for accessing data:

| Address | Purpose |
|---------|---------|
| `/api/products` | Get list of all available products |
| `/api/candles` | Get price chart data for a product |
| `/api/orderbook` | Get current buy/sell orders for a product |

## 💡 Custom Algorithms

You can write your own JavaScript functions to analyze the data. Check out `example.js` for sample algorithms including:

- Moving averages
- RSI indicator
- Bollinger Bands
- MACD
- Custom trading strategies

## 🤝 Contributing

Feel free to suggest improvements or report issues. This project is built with modern web technologies and follows clean coding practices.

---

*Track Hypixel Skyblock bazaar prices with live charts and custom analysis tools*