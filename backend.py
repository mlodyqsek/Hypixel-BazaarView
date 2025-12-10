import requests
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime, timedelta
import time

def setup_database():
    """Sets up the database and creates all necessary tables"""
    # Connect to the default PostgreSQL database to create the bazaar_db database
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="password",
        host="localhost"
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Create the bazaar_db database if it doesn't already exist
    cur.execute("SELECT 1 FROM pg_database WHERE datname='bazaar_db'")
    if not cur.fetchone():
        cur.execute("CREATE DATABASE bazaar_db")
        print("Database 'bazaar_db' created successfully")

    cur.close()
    conn.close()

    # Now connect to the newly created bazaar_db
    conn = psycopg2.connect(
        dbname="bazaar_db",
        user="postgres",
        password="password",
        host="localhost"
    )
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_book_snapshot (
            product_id VARCHAR(50) NOT NULL,
            timestamp TIMESTAMPTZ NOT NULL,
            side VARCHAR(4) NOT NULL,
            rank INT NOT NULL,
            price DECIMAL(15,2) NOT NULL,
            amount BIGINT NOT NULL,
            orders INT NOT NULL,
            PRIMARY KEY (product_id, timestamp, side, rank)
        );
        CREATE INDEX IF NOT EXISTS idx_orderbook_cleanup 
        ON order_book_snapshot(timestamp);
        CREATE INDEX IF NOT EXISTS idx_orderbook_product_time 
        ON order_book_snapshot(product_id, timestamp, side, rank);
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS candles (
            id SERIAL PRIMARY KEY,
            product_id VARCHAR(50) NOT NULL,
            timestamp TIMESTAMPTZ NOT NULL,
            open DECIMAL(15,2),
            high DECIMAL(15,2),
            low DECIMAL(15,2),
            close DECIMAL(15,2),
            buy_volume BIGINT,
            sell_volume BIGINT,
            UNIQUE(product_id, timestamp)
        );
        CREATE INDEX IF NOT EXISTS idx_candles_product_time 
        ON candles(product_id, timestamp DESC);
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("Database tables created successfully")

def fetch_bazaar_data():
    """Retrieves the latest bazaar data from the Hypixel API"""
    try:
        response = requests.get("https://api.hypixel.net/skyblock/bazaar", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def filter_and_extract_products(data):
    """Processes the raw data to filter active products and get their top buy/sell orders"""
    if not data or 'products' not in data:
        return []
    
    filtered_products = []
    timestamp = datetime.now()
    
    for product_id, product_data in data['products'].items():
        buy_summary = product_data.get('buy_summary', [])
        sell_summary = product_data.get('sell_summary', [])
        
        if not buy_summary or not sell_summary:
            continue
        
        top_buy_price = buy_summary[0]['pricePerUnit']
        top_sell_price = sell_summary[0]['pricePerUnit']
        
        if top_buy_price < 0.7 or top_sell_price < 0.7:
            continue
        
        product_info = {
            'product_id': product_id,
            'timestamp': timestamp,
            'buy_orders': buy_summary[:5],
            'sell_orders': sell_summary[:5]
        }
        filtered_products.append(product_info)

    print(f"Filtered to {len(filtered_products)} active products")
    return filtered_products

def store_order_book_snapshot(products):
    """Saves the order book information to the database"""
    if not products:
        return
    
    conn = psycopg2.connect(
        dbname="bazaar_db",
        user="postgres",
        password="password",
        host="localhost"
    )
    cur = conn.cursor()
    
    rows = []
    for product in products:
        product_id = product['product_id']
        timestamp = product['timestamp']
        
        for rank, order in enumerate(product['buy_orders'], start=1):
            rows.append((
                product_id,
                timestamp,
                'BUY',
                rank,
                order['pricePerUnit'],
                order['amount'],
                order['orders']
            ))
        
        for rank, order in enumerate(product['sell_orders'], start=1):
            rows.append((
                product_id,
                timestamp,
                'SELL',
                rank,
                order['pricePerUnit'],
                order['amount'],
                order['orders']
            ))
    
    execute_batch(cur, """
        INSERT INTO order_book_snapshot 
        (product_id, timestamp, side, rank, price, amount, orders)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """, rows)
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"Stored {len(rows)} order book entries")

def generate_candles(interval_minutes=1):
    """Creates candlestick data using OHLC calculations and removes outdated order book entries"""
    conn = psycopg2.connect(
        dbname="bazaar_db",
        user="postgres",
        password="password",
        host="localhost"
    )
    cur = conn.cursor()
    
    now = datetime.now()
    cutoff_time = now - timedelta(minutes=interval_minutes)

    # Get all unique products that have data within the specified time interval
    cur.execute("""
        SELECT DISTINCT product_id
        FROM order_book_snapshot
        WHERE timestamp >= %s
    """, (cutoff_time,))
    
    products = [row[0] for row in cur.fetchall()]
    
    candles_created = 0
    for product_id in products:
        # Calculate Open, High, Low, Close prices and volumes for the buy side
        cur.execute("""
            WITH price_sequence AS (
                SELECT 
                    timestamp,
                    price,
                    amount,
                    ROW_NUMBER() OVER (ORDER BY timestamp ASC) as row_num,
                    COUNT(*) OVER () as total_rows
                FROM order_book_snapshot
                WHERE product_id = %s 
                AND timestamp >= %s
                AND side = 'BUY'
                AND rank = 1
                ORDER BY timestamp ASC
            )
            SELECT 
                MAX(CASE WHEN row_num = 1 THEN timestamp END) as first_timestamp,
                MAX(CASE WHEN row_num = total_rows THEN timestamp END) as last_timestamp,
                MAX(CASE WHEN row_num = 1 THEN price END) as open_price,
                MAX(price) as high_price,
                MIN(price) as low_price,
                MAX(CASE WHEN row_num = total_rows THEN price END) as close_price,
                SUM(amount) as buy_volume,
                COUNT(*) as data_points
            FROM price_sequence
        """, (product_id, cutoff_time))
        
        result = cur.fetchone()
        if not result or result[0] is None:
            continue
        
        first_timestamp, last_timestamp, open_price, high_price, low_price, close_price, buy_volume, data_points = result

        # Retrieve the sell volume data
        cur.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM order_book_snapshot
            WHERE product_id = %s 
            AND timestamp >= %s
            AND side = 'SELL'
            AND rank = 1
        """, (product_id, cutoff_time))
        
        sell_volume = cur.fetchone()[0] or 0

        # Set the timestamp for this candle, aligned to the collection interval
        candle_timestamp = last_timestamp

        # Add this candle to the database or update if it already exists
        cur.execute("""
            INSERT INTO candles 
            (product_id, timestamp, open, high, low, close, buy_volume, sell_volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (product_id, timestamp) 
            DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                buy_volume = EXCLUDED.buy_volume,
                sell_volume = EXCLUDED.sell_volume
        """, (product_id, candle_timestamp, open_price, high_price, low_price, close_price, 
              buy_volume, sell_volume))
        
        candles_created += 1

    # Remove old order book snapshots to keep the database clean
    cur.execute("""
        DELETE FROM order_book_snapshot
        WHERE timestamp < %s
    """, (cutoff_time,))

    deleted_rows = cur.rowcount

    conn.commit()
    cur.close()
    conn.close()

    print(f"Generated {candles_created} candles")
    print(f"Cleaned up {deleted_rows} old order book entries")

def run_collection_loop(fetch_interval=60, candle_interval=5):
    """The main processing loop that continuously fetches and processes bazaar data"""
    print("Starting Bazaar Data Pipeline")
    print(f"Fetch interval: {fetch_interval}s")
    print(f"Candle interval: {candle_interval}min")
    print("Press Ctrl+C to stop\n")
    
    last_candle_time = datetime.now()
    
    try:
        while True:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Fetching bazaar data...")
            data = fetch_bazaar_data()

            if data:
                products = filter_and_extract_products(data)
                store_order_book_snapshot(products)

            minutes_since_last_candle = (datetime.now() - last_candle_time).total_seconds() / 60

            if minutes_since_last_candle >= candle_interval:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Generating candles...")
                generate_candles(interval_minutes=candle_interval)
                last_candle_time = datetime.now()

            time.sleep(fetch_interval)

    except KeyboardInterrupt:
        print("\n\nStopped by user")

if __name__ == "__main__":
    setup_database()
    run_collection_loop(fetch_interval=60, candle_interval=1)   