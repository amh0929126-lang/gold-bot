import time
import requests
import pandas as pd
import numpy as np

BOT_TOKEN = "8904195876:AAGh6Mc_tMqN1Mqf0P-Gveo1NdS1AXdgFIA"
CHAT_ID = "7149103037"
SYMBOL = "PAXGUSDT"
TIMEFRAME = "5m"
CHECK_INTERVAL = 10 

EMA_PERIOD = 7
RSI_PERIOD = 14
SUPERTREND_PERIOD = 10
SUPERTREND_MULTIPLIER = 3.0

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram Error: {e}")

def get_klines(symbol, interval, limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        if isinstance(data, list) and len(data) > 0:
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'
            ])
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            return df
    except Exception as e:
        print(f"Binance API Error: {e}")
    return None

def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_supertrend(df, period=10, multiplier=3.0):
    high, low, close = df['high'], df['low'], df['close']
    tr1 = pd.DataFrame(high - low)
    tr2 = pd.DataFrame(abs(high - close.shift(1)))
    tr3 = pd.DataFrame(abs(low - close.shift(1)))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/period, adjust=False).mean()

    hl2 = (high + low) / 2
    basic_upperband = hl2 + (multiplier * atr)
    basic_lowerband = hl2 - (multiplier * atr)

    upperband = basic_upperband.copy()
    lowerband = basic_lowerband.copy()
    direction = np.zeros(len(df))

    for i in range(1, len(df)):
        if basic_upperband.iloc[i] < upperband.iloc[i-1] or close.iloc[i-1] > upperband.iloc[i-1]:
            upperband.iloc[i] = basic_upperband.iloc[i]
        else:
            upperband.iloc[i] = upperband.iloc[i-1]

        if basic_lowerband.iloc[i] > lowerband.iloc[i-1] or close.iloc[i-1] < lowerband.iloc[i-1]:
            lowerband.iloc[i] = basic_lowerband.iloc[i]
        else:
            lowerband.iloc[i] = lowerband.iloc[i-1]

        if close.iloc[i] > upperband.iloc[i-1]:
            direction[i] = 1
        elif close.iloc[i] < lowerband.iloc[i-1]:
            direction[i] = -1
        else:
            direction[i] = direction[i-1]

    return pd.Series(direction, index=df.index)

def main():
    print("🚀 Pullback & Re-entry Strategy Bot Active...")
    send_telegram(f"⚡ *Advanced Re-entry Strategy Bot Active*\nPair: `{SYMBOL}`\nTimeframe: `{TIMEFRAME}`")
    
    in_position = False
    in_pullback = False

    while True:
        df = get_klines(SYMBOL, TIMEFRAME)
        if df is not None and len(df) >= 30:
            df['ema7'] = df['close'].ewm(span=EMA_PERIOD, adjust=False).mean()
            df['rsi'] = calculate_rsi(df, RSI_PERIOD)
            df['st_direction'] = calculate_supertrend(df, SUPERTREND_PERIOD, SUPERTREND_MULTIPLIER)

            curr = df.iloc[-1]
            prev = df.iloc[-2]

            price = curr['close']
            ema = curr['ema7']
            rsi = curr['rsi']
            st_dir = curr['st_direction']

            if st_dir != prev['st_direction']:
                in_position = False
                in_pullback = False

            if st_dir == 1:
                if (price <= ema or rsi < 48) and not in_pullback:
                    in_pullback = True

                if in_pullback and price > ema and rsi > 50:
                    msg = f"🟢 *RE-ENTRY BUY SIGNAL (PAXG/USDT)*\nReason: Ended Pullback & Bounced!\nPrice: `${price:.2f}`\nEMA 7: `${ema:.2f}`\nRSI: `{rsi:.1f}`"
                    send_telegram(msg)
                    in_pullback = False
                    in_position = True

            elif st_dir == -1:
                if (price >= ema or rsi > 52) and not in_pullback:
                    in_pullback = True

                if in_pullback and price < ema and rsi < 50:
                    msg = f"🔴 *RE-ENTRY SELL SIGNAL (PAXG/USDT)*\nReason: Ended Pullback & Rejected!\nPrice: `${price:.2f}`\nEMA 7: `${ema:.2f}`\nRSI: `{rsi:.1f}`"
                    send_telegram(msg)
                    in_pullback = False
                    in_position = True

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
