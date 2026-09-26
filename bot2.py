import os
import time
import requests
import pandas as pd
import threading
from flask import Flask, render_template_string

app = Flask(__name__)

# إعدادات التداول
SYMBOL = "PAXGUSDT"
TIMEFRAME = "5m"
CHECK_INTERVAL = 300  # كل 5 دقائق

# متغيرات لتخزين أحدث حالة للسوق
market_data = {
    "price": "جاري التحميل...",
    "ema": "---",
    "rsi": "---",
    "supertrend": "---",
    "signal": "NEUTRAL",
    "time": "---"
}

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
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
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

def market_monitor_loop():
    global market_data
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

            if price > ema and rsi > 50 and price > st:
                signal = "BUY"
            elif price < ema and rsi < 50 and price < st:
                signal = "SELL"
            else:
                signal = "NEUTRAL"

            market_data = {
                "price": f"{price:,.2f}",
                "ema": f"{ema:.2f}",
                "rsi": f"{rsi:.2f}",
                "supertrend": f"{st:.2f}",
                "signal": signal,
                "time": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
            }
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(CHECK_INTERVAL)

# تصميم واجهة الويب المتوافقة مع الهواتف
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مراقب الذهب - Gold Tracker</title>
    <meta http-equiv="refresh" content="60">
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #0f172a; color: #f8fafc; text-align: center; padding: 20px; margin: 0; }
        .card { background: #1e293b; border-radius: 15px; padding: 20px; max-width: 400px; margin: auto; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        h1 { color: #38bdf8; font-size: 20px; margin-bottom: 10px; }
        .price { font-size: 30px; font-weight: bold; color: #fbbf24; margin: 15px 0; }
        .signal-BUY { background-color: #166534; color: #dcfce7; padding: 10px; border-radius: 8px; font-weight: bold; font-size: 18px; }
        .signal-SELL { background-color: #991b1b; color: #fee2e2; padding: 10px; border-radius: 8px; font-weight: bold; font-size: 18px; }
        .signal-NEUTRAL { background-color: #334155; color: #cbd5e1; padding: 10px; border-radius: 8px; font-weight: bold; font-size: 18px; }
        .info { margin: 12px 0; font-size: 14px; display: flex; justify-content: space-between; padding: 8px 10px; background: #0f172a; border-radius: 5px; }
        .footer { font-size: 11px; color: #94a3b8; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🥇 مراقب سوق الذهب PAXG/USDT</h1>
        <div class="price">{{ data.price }} USDT</div>
        
        <div class="signal-{{ data.signal }}">
            الإشارة الحالية: {{ data.signal }}
        </div>

        <div style="margin-top: 20px;">
            <div class="info"><span>مؤشر EMA (7):</span> <strong>{{ data.ema }}</strong></div>
            <div class="info"><span>مؤشر RSI (14):</span> <strong>{{ data.rsi }}</strong></div>
            <div class="info"><span>مؤشر SuperTrend:</span> <strong>{{ data.supertrend }}</strong></div>
        </div>

        <div class="footer">آخر تحديث: {{ data.time }} (UTC)<br>التحديث تلقائي كل دقيقة</div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, data=market_data)

if __name__ == "__main__":
    t = threading.Thread(target=market_monitor_loop)
    t.daemon = True
    t.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
