import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import time

# 1. إعدادات اللوحة الفنية وتطابق التصميم والألوان مع نموذجك المفضل
st.set_page_config(page_title="صائد الموجات (نظام الحماية الذكي)", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #f8fafc; }
    
    /* شريط الحالة البرتقالي ACTIVE */
    .header-banner {
        background-color: #ff6b00; color: #ffffff; padding: 10px; 
        border-radius: 6px; text-align: center; font-weight: bold; 
        font-size: 14px; letter-spacing: 0.5px; margin-bottom: 20px;
    }
    
    /* صناديق الحالات الفنية المقوسة والملونة لشروط الدخول */
    .box-buy {
        border: 1px solid #10b981; background-color: rgba(16, 185, 129, 0.05);
        border-radius: 12px; padding: 18px; text-align: center; color: #10b981;
        font-size: 18px; font-weight: bold; margin-bottom: 15px;
    }
    .box-sell {
        border: 1px solid #ef4444; background-color: rgba(239, 68, 68, 0.05);
        border-radius: 12px; padding: 18px; text-align: center; color: #ef4444;
        font-size: 18px; font-weight: bold; margin-bottom: 15px;
    }
    .box-hold {
        border: 1px dashed #4b5563; background-color: #111827;
        border-radius: 12px; padding: 18px; text-align: center; color: #94a3b8;
        font-size: 16px; margin-bottom: 15px;
    }
    
    .condition-box {
        border: 1px dashed #38bdf8; background-color: rgba(56, 189, 248, 0.03);
        border-radius: 8px; padding: 12px; text-align: center; color: #38bdf8;
        font-size: 15px; font-weight: bold; margin-bottom: 20px;
    }
    
    /* كروت عرض البيانات الرقمية المتناسقة والمصفوفة بدقة */
    .data-card {
        background-color: #111827; border: 1px solid #1f2937;
        border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 12px;
        min-height: 70px; display: flex; flex-direction: column; justify-content: center;
    }
    .data-inner { display: flex; justify-content: space-around; align-items: center; width: 100%; }
    .data-label { color: #94a3b8; font-size: 13px; font-weight: 500; }
    .data-value { color: #ffffff; font-size: 18px; font-weight: bold; }
    
    /* صناديق مستويات الأهداف ووقف الخسارة الجذابة */
    .target-box {
        background-color: #111827; border: 1px solid #1f2937; border-radius: 8px;
        padding: 10px; text-align: center; margin-bottom: 20px;
    }
    .target-title { color: #64748b; font-size: 12px; margin-bottom: 4px; font-weight: 500; }
    .target-val-sl { color: #f87171; font-size: 16px; font-weight: bold; }
    .target-val-tp { color: #4ade80; font-size: 16px; font-weight: bold; }
    
    /* صندوق التوجيه المنهجي السفلي */
    .info-box {
        border: 1px solid #1f2937; background-color: rgba(17, 24, 39, 0.6);
        border-radius: 8px; padding: 12px; font-size: 13px; line-height: 1.5; color: #f3f4f6;
    }
    </style>
""", unsafe_allow_html=True)

def play_sound():
    sound_html = '<iframe src="https://mixkit.co" allow="autoplay" style="display:none" id="iframeAudio"></iframe>'
    st.markdown(sound_html, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #38bdf8; font-weight: bold; font-size: 24px;'>⚡ صائد الموجات (نظام الحماية الذكي)</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 13px; margin-bottom: 20px;'>مفعل بنجاح (RSI 70/30) فلتر التصحيح والتشبع الدقيق للذهب الحقيقي</p>", unsafe_allow_html=True)

# تغذية السعر الفوري لـ XAU/USD المباشر بدلاً من الرموز المضللة بالبورصات الأخرى
ticker = "XAUUSD=X" 
timeframe = "5m" 

@st.cache_data(ttl=2) # تم تقليل التجميد لـ 2 ثانية لبث السعر والشموع لحظياً وبدون أي تأخير
def fetch_live_gold():
    df = yf.download(tickers=ticker, period="3d", interval=timeframe, progress=False)
    if not df.empty and isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    return df

df = fetch_live_gold()

if df.empty or len(df) < 15:
    st.markdown("<div class='box-hold'>🔄 جاري مزامنة النبضات السعرية والمؤشرات الفنية للذهب مع المنصة...</div>", unsafe_allow_html=True)
else:
    # 1. حساب المتوسط المتحرك الأسي EMA 7 المطابق لحركة الشموع
    df['EMA_7'] = df['Close'].ewm(span=7, adjust=False).mean()
    
    # 2. حساب مؤشر القوة النسبية RSI 14 الدقيق للتصحيحات
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    rs = gain / (loss + 1e-10)
    df['RSI_14'] = 100 - (100 / (1 + rs))
    
    # 3. حساب خوارزمية السوبر تريند الرسمية (ATR 10, Multiplier 3)
    period = 10
    multiplier = 3
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    df['ATR'] = true_range.ewm(alpha=1/period, adjust=False).mean()
    
    hl2 = (df['High'] + df['Low']) / 2
    df['Basic_UB'] = hl2 + (multiplier * df['ATR'])
    df['Basic_LB'] = hl2 - (multiplier * df['ATR'])
    df['Final_UB'] = df['Basic_UB']
    df['Final_LB'] = df['Basic_LB']
    df['ST_Line'] = 0.0
    df['ST_Dir'] = 1
    
    for i in range(1, len(df)):
        if df['Basic_UB'].iloc[i] < df['Final_UB'].iloc[i-1] or df['Close'].iloc[i-1] > df['Final_UB'].iloc[i-1]:
            df.iloc[i, df.columns.get_loc('Final_UB')] = df['Basic_UB'].iloc[i]
        else:
            df.iloc[i, df.columns.get_loc('Final_UB')] = df['Final_UB'].iloc[i-1]
            
        if df['Basic_LB'].iloc[i] > df['Final_LB'].iloc[i-1] or df['Close'].iloc[i-1] < df['Final_LB'].iloc[i-1]:
            df.iloc[i, df.columns.get_loc('Final_LB')] = df['Basic_LB'].iloc[i]
        else:
            df.iloc[i, df.columns.get_loc('Final_LB')] = df['Final_LB'].iloc[i-1]
            
        if df['Close'].iloc[i] > df['Final_UB'].iloc[i-1]:
            df.iloc[i, df.columns.get_loc('ST_Dir')] = 1
        elif df['Close'].iloc[i] < df['Final_LB'].iloc[i-1]:
            df.iloc[i, df.columns.get_loc('ST_Dir')] = -1
        else:
            df.iloc[i, df.columns.get_loc('ST_Dir')] = df['ST_Dir'].iloc[i-1]
            
        if df['ST_Dir'].iloc[i] == 1:
            df.iloc[i, df.columns.get_loc('ST_Line')] = df['Final_LB'].iloc[i]
        else:
            df.iloc[i, df.columns.get_loc('ST_Line')] = df['Final_UB'].iloc[i]

    # قراءة بيانات آخر شمعة حركية حية لمطابقة الأرقام في المنصة
    last_candle = df.iloc[-1]
    current_price = round(float(last_candle['Close']), 2)
    ema_val = round(float(last_candle['EMA_7']), 2)
    rsi_val = round(float(last_candle['RSI_14']), 2)
    st_dir = int(last_candle['ST_Dir'])
    st_line = round(float(last_candle['ST_Line']), 2)
    atr_val = float(last_candle['ATR'])
    
    # حساب أهداف وقف الخسارة الدقيقة المفلترة بالتذبذب
    tp1_buy = round(current_price + (atr_val * 1.5), 2)
    tp2_buy = round(current_price + (atr_val * 3.0), 2)
    sl_buy = round(st_line, 2)
    
    tp1_sell = round(current_price - (atr_val * 1.5), 2)
    tp2_sell = round(current_price - (atr_val * 3.0), 2)
    sl_sell = round(st_line, 2)

    # فلترة وإصدار الإشارات بناءً على وضع الزخم والاتجاه
    signal_status = "hold"
    if st_dir == 1:
        if current_price > ema_val and rsi_val < 70:
            signal_status = "buy"
    elif st_dir == -1:
        if current_price < ema_val and rsi_val > 30:
            signal_status = "sell"

    # 1. شريط الحماية والتشبع (ACTIVE)
    st.markdown("<div class='header-banner'>⚡ SMART CORRECTION & RSI FILTER ACTIVE</div>", unsafe_allow_html=True)
    
    # 2. كتل وصناديق الحالات الفنية المطابقة للنموذج المطلوب
    if signal_status == "buy":
        st.markdown("<div class='box-buy'>🟢 فرصة شراء متاحة (تصحيح بسيط مقبول)</div>", unsafe_allow_html=True)
        st.markdown("<div class='condition-box'>🚀 شروط الاستراتيجية مكتملة (اقتنص الفرصة بلا تردد)</div>", unsafe_allow_html=True)
        play_sound()
    elif signal_status == "sell":
        st.markdown("<div class='box-sell'>🔴 فرصة بيع متاحة (استمرار هبوط مؤكد)</div>", unsafe_allow_html=True)
        st.markdown("<div class='condition-box'>📉 شروط الاستراتيجية مكتملة بيعاً (اقتنص الفرصة)</div>", unsafe_allow_html=True)
        play_sound()
    else:
        st.markdown("<div class='box-hold'>⚪ وضع الانتظار والمراقبة مستمرة الآن على فريم 5 دقائق</div>", unsafe_allow_html=True)
        st.markdown("<div class='condition-box'>🔍 المحرك الآلي يراقب الأسعار... انتظر اكتمال الشروط بالكامل</div>", unsafe_allow_html=True)

    # 3. عرض الأرقام الفنية والمؤشرات في عمودين متناسقين تماماً كالمنصة
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"<div class='data-card'><div class='data-inner'><span class='data-label'>السعر:</span><span class='data-value'>{current_price}</span></div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='data-card'><div class='data-inner'><span class='data-label'>RSI 14:</span><span class='data-value'>{rsi_val}</span></div></div>", unsafe_allow_html=True)
    with col_b:
        st.markdown(f"<div class='data-card'><div class='data-inner'><span class='data-label'>EMA 7:</span><span class='data-value'>{ema_val}</span></div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='data-card'><div class='data-inner'><span class='data-label'>التريند:</span><span class='data-value'>{'صاعد' if st_dir == 1 else 'هابط'}</span></div></div>", unsafe_allow_html=True)

    st.write("")
    
    # 4. مستويات وقف الخسارة والأهداف مصفوفة أفقياً
    col_sl, col_tp1, col_tp2 = st.columns(3)
    if st_dir == 1 or signal_status == "buy":
        with col_sl: st.markdown(f"<div class='target-box'><div class='target-title'>وقف الخسارة</div><div class='target-val-sl'>{sl_buy}</div></div>", unsafe_allow_html=True)
