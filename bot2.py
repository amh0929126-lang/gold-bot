import os
import time
import requests
import pandas as pd
import numpy as np
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# ==========================================
# 1. خادم ويب صوري لتجاوز فحص Render Port
# ==========================================
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Web server starting on port {port}...")
    httpd.serve_forever()

# تشغيل السيرفر الوهمي في الخلفية
server_thread = threading.Thread(target=run_web_server)
server_thread.daemon = True
server_thread.start()

# ==========================================
# 2. إعدادات التداول والمتغيرات
# ==========================================
SYMBOL = "PAXGUSDT"
TIMEFRAME = "5m"
CHECK_INTERVAL = 300  # كل 5 دقائق

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram Token or Chat ID missing!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def get_klines(symbol, interval, limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url, timeout=10)
    data = response.json()
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['close'] = df['close'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    return df

def calculate_ema(df, period=7):
    return df['close'].ewm(span=period, adjust=False).mean()

def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_supertrend(df, period=10, multiplier=3):
    high = df['high']
    low = df['low']
    close = df['close']
    
    tr1 = pd.DataFrame(high - low)
    tr2 = pd.DataFrame(abs(high - close.shift(1)))
    tr3 = pd.DataFrame(abs(low - close.shift(1)))
    frames = [tr1, tr2, tr3]
    tr = pd.concat(frames, axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/period, adjust=False).mean()

    hl2 = (high + low) / 2
    final_upperband = hl2 + (multiplier * atr)
    final_lowerband = hl2 - (multiplier * atr)

    supertrend = pd.Series(index=df.index, dtype=float)
    for i in range(1, len(df)):
        if close[i] > final_upperband[i-1]:
            supertrend[i] = final_lowerband[i]
        else:
            supertrend[i] = final_upperband[i]
    return supertrend

def main():
    last_signal = None
    print("Bot started monitoring market...")
    
    while True:
        try:
            df = get_klines(SYMBOL, TIMEFRAME)
            df['ema'] = calculate_ema(df, 7)
            df['rsi'] = calculate_rsi(df, 14)
            df['supertrend'] = calculate_supertrend(df)

            last_row = df.iloc[-1]
            price = last_row['close']
            ema = last_row['ema']
            rsi = last_row['rsi']
            st = last_row['supertrend']

            # إشارات الشراء والبيع
            if price > ema and rsi > 50 and price > st:
                signal = "BUY"
            elif price < ema and rsi < 50 and price < st:
                signal = "SELL"
            else:
                signal = "NEUTRAL"

            if signal != last_signal and signal != "NEUTRAL":
                msg = (f"🚨 **Signal {signal} detected!**\n"
                       f"Prix: {price}\n"
                       f"EMA (7): {ema:.2f}\n"
                       f"RSI (14): {rsi:.2f}\n"
                       f"SuperTrend: {st:.2f}")
                send_telegram(msg)
                last_signal = signal

        except Exception as e:
            print(f"Erreur dans la boucle: {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    send_telegram("⚡ **Advanced Re-entry Strategy Bot Active**\nPair: PAXGUSDT\nTimeframe: 5m\n\n🚀 تم تشغيل البوت بنجاح وهو الآن يراقب السوق 24/7!")
    main()
