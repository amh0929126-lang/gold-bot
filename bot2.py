import os
import time
import requests
import pandas as pd
import numpy as np
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# ==========================================
# 1. خادم ويب صوري لتجاوز فحص Render المجاني
# ==========================================
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

# تشغيل خادم المنفذ في الخلفية
threading.Thread(target=run_web_server, daemon=True).start()

# ==========================================
# 2. إعدادات التليجرام والزوج من البيئة
# ==========================================
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = "7149103037"
SYMBOL = "PAXGUSDT"
TIMEFRAME = "5m"
CHECK_INTERVAL = 10

EMA_PERIOD = 7
RSI_PERIOD = 14
SUPERTREND_PERIOD = 10
SUPERTREND_MULTIPLIER = 3.0

def send_telegram(message):
    if not BOT_TOKEN:
        print("Telegram Token non configuré dans Render!")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Erreur d'envoi Telegram: {e}")

def get_klines(symbol, interval, limit=100):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        df = pd.DataFrame(data, columns=[
            'time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'
        ])
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        return df
    except Exception as e:
        print(f"Erreur Récupération Données: {e}")
        return None

def calculate_ema(df, period):
    return df['close'].ewm(span=period, adjust=False).mean()

def calculate_rsi(df, period):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_supertrend(df, period, multiplier):
    high = df['high']
    low = df['low']
    close = df['close']
    
    price_diff1 = high - low
    price_diff2 = abs(high - close.shift(1))
    price_diff3 = abs(low - close.shift(1))
    
    tr = pd.concat([price_diff1, price_diff2, price_diff3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    
    hl2 = (high + low) / 2
    basic_upperband = hl2 + (multiplier * atr)
    basic_lowerband = hl2 - (multiplier * atr)
    
    upperband = basic_upperband.copy()
    lowerband = basic_lowerband.copy()
    
    for i in range(1, len(df)):
        if basic_upperband.iloc[i] < upperband.iloc[i-1] or close.iloc[i-1] > upperband.iloc[i-1]:
            upperband.iloc[i] = basic_upperband.iloc[i]
        else:
            upperband.iloc[i] = upperband.iloc[i-1]
            
        if basic_lowerband.iloc[i] > lowerband.iloc[i-1] or close.iloc[i-1] < lowerband.iloc[i-1]:
            lowerband.iloc[i] = basic_lowerband.iloc[i]
        else:
            lowerband.iloc[i] = lowerband.iloc[i-1]
            
    st = pd.Series(index=df.index, dtype=float)
    st.iloc[0] = upperband.iloc[0]
    
    for i in range(1, len(df)):
        if st.iloc[i-1] == upperband.iloc[i-1]:
            st.iloc[i] = lowerband.iloc[i] if close.iloc[i] > upperband.iloc[i] else upperband.iloc[i]
        else:
            st.iloc[i] = upperband.iloc[i] if close.iloc[i] < lowerband.iloc[i] else lowerband.iloc[i]
            
    return st

def main():
    send_telegram(f"🤖 Bot PAXG/USDT Démarré 24/7 sur Render!")
    last_signal = None
    
    while True:
        try:
            df = get_klines(SYMBOL, TIMEFRAME)
            if df is not None and not df.empty:
                df['ema'] = calculate_ema(df, EMA_PERIOD)
                df['rsi'] = calculate_rsi(df, RSI_PERIOD)
                df['supertrend'] = calculate_supertrend(df, SUPERTREND_PERIOD, SUPERTREND_MULTIPLIER)
                
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
                    msg = (f"🚨 **Signal {signal} sur PAXG/USDT (5m)**\n\n"
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
    main()
