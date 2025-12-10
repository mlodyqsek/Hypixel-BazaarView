from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import psycopg2
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

def get_db():
    return psycopg2.connect(
        dbname="bazaar_db",
        user="postgres",
        password="password",
        host="localhost"
    )

@app.route('/')
def index():
    return send_file('frontend.html')

@app.route('/api/products')
def get_products():
    """Retrieves the list of products currently available in the bazaar"""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT product_id FROM candles ORDER BY product_id")
        products = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify(products)
    except Exception as e:
        print(f"Error in /api/products: {e}")
        return jsonify([])

@app.route('/api/candles')
def get_candles():
    """Fetches candlestick chart data for the specified product"""
    try:
        product = request.args.get('product')
        hours = int(request.args.get('hours', 1))
        
        if not product:
            return jsonify({'error': 'Product parameter required'}), 400
        
        conn = get_db()
        cur = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        cur.execute("""
            SELECT timestamp, open, high, low, close, buy_volume, sell_volume
            FROM candles
            WHERE product_id = %s
            AND timestamp >= %s
            ORDER BY timestamp ASC
        """, (product, cutoff_time))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        if not rows:
            return jsonify({'error': 'No data available for this product', 'candles': []})
        
        candles = []
        for row in rows:
            candles.append({
                'timestamp': row[0].strftime('%Y-%m-%d %H:%M:%S'),
                'open': float(row[1]),
                'high': float(row[2]),
                'low': float(row[3]),
                'close': float(row[4]),
                'buy_volume': int(row[5]),
                'sell_volume': int(row[6])
            })
        
        return jsonify({'candles': candles})
    
    except Exception as e:
        print(f"Error in /api/candles: {e}")
        return jsonify({'error': str(e), 'candles': []})

@app.route('/api/orderbook')
def get_orderbook():
    """Retrieves the most recent order book information for a given product"""
    try:
        product = request.args.get('product')
        
        if not product:
            return jsonify({'error': 'Product parameter required'}), 400
        
        conn = get_db()
        cur = conn.cursor()
        
        # Find the most recent timestamp available for this product
        cur.execute("""
            SELECT MAX(timestamp)
            FROM order_book_snapshot
            WHERE product_id = %s
        """, (product,))
        
        latest_time = cur.fetchone()[0]
        
        if not latest_time:
            cur.close()
            conn.close()
            return jsonify({'buy_orders': [], 'sell_orders': []})
        
        # Get the top 5 buy orders
        cur.execute("""
            SELECT price, amount, orders
            FROM order_book_snapshot
            WHERE product_id = %s
            AND timestamp = %s
            AND side = 'BUY'
            ORDER BY rank ASC
            LIMIT 5
        """, (product, latest_time))
        
        buy_orders = []
        for row in cur.fetchall():
            buy_orders.append({
                'price': float(row[0]),
                'amount': int(row[1]),
                'orders': int(row[2])
            })
        
        # Get the top 5 sell orders
        cur.execute("""
            SELECT price, amount, orders
            FROM order_book_snapshot
            WHERE product_id = %s
            AND timestamp = %s
            AND side = 'SELL'
            ORDER BY rank ASC
            LIMIT 5
        """, (product, latest_time))
        
        sell_orders = []
        for row in cur.fetchall():
            sell_orders.append({
                'price': float(row[0]),
                'amount': int(row[1]),
                'orders': int(row[2])
            })
        
        cur.close()
        conn.close()
        
        return jsonify({
            'buy_orders': buy_orders,
            'sell_orders': sell_orders
        })
    
    except Exception as e:
        print(f"Error in /api/orderbook: {e}")
        return jsonify({'error': str(e), 'buy_orders': [], 'sell_orders': []})

if __name__ == '__main__':
    app.run(debug=True, port=5000)