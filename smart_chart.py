import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import time

# 1. إعدادات اللوحة الفنية الاحترافية الرقمية الصافية للذهب
st.set_page_config(page_title="صائد الموجات (نظام الحماية الذكي)", page_icon="🏆", layout="centered")

# تصميم CSS فاخر ومظلم يطابق تماماً الصورة المرفقة في طلبك
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #f8fafc; }
    
    /* تصميم عنوان التوجيه العالي الملون */
    .header-banner {
        background-color: #ff6b00; color: #ffffff; padding: 12px; 
        border-radius: 8px; text-align: center; font-weight: bold; 
        font-size: 16px; letter-spacing: 1px; margin-bottom: 25px;
    }
    
    /* صناديق الحالات الفنية الملونة */
    .box-buy {
        border: 2px solid #10b981; background-color: rgba(16, 185, 129, 0.1);
        border-radius: 12px; padding: 20px; text-align: center; color: #10b981;
        font-size: 20px; font-weight: bold; margin-bottom: 15px;
    }
    .box-sell {
        border: 2px solid #ef4444; background-color: rgba(239, 68, 68, 0.1);
        border-radius: 12px; padding: 20px; text-align: center; color: #ef4444;
        font-size: 20px; font-weight: bold; margin-bottom: 15px;
    }
    .box-hold {
        border: 1px dashed #64748b; background-color: #1e293b;
        border-radius: 12px; padding: 20px; text-align: center; color: #94a3b8;
        font-size: 18px; margin-bottom: 15px;
    }
    
    /* صندوق الشروط المتقطعة */
    .condition-box {
        border: 1px dashed #38bdf8; background-color: rgba(56, 189, 248, 0.05);
        border-radius: 10px; padding: 15px; text-align: center; color: #38bdf8;
        font-size: 16px; font-weight: bold; margin-bottom: 25px;
    }
    
    /* كروت عرض البيانات الرقمية */
    .data-card {
        background-color: #121826; border: 1px solid #1e293b;
        border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 15px;
    }
    .data-label { color: #94a3b8; font-size: 14px; }
    .data-value { color: #f8fafc; font-size: 20px; font-weight: bold; margin-top: 5px; }
    
    /* صناديق أرقام الأهداف ووقف الخسارة */
    .target-sl { color: #f87171; font-size: 18px; font-weight: bold; text-align: center; }
    .target-tp { color: #4ade80; font-size: 18px; font-weight: bold; text-align: center; }
    
    /* صندوق التوجيه المنهجي السفلي */
    .info-box {
        border: 1px solid #1e293b; background-color: rgba(30, 41, 59, 0.5);
        border-radius: 10px; padding: 15px; font-size: 14px; line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

# دالة لتشغيل صوت التنبيه التلقائي للمتداول عند صدور الفرصة
def play_sound():
    sound_html = '<iframe src="https://mixkit.co" allow="autoplay" style="display:none" id="iframeAudio"></iframe>'
    st.markdown(sound_html, unsafe_allow_html=True)

# واجهة المستخدم الرئيسية الموحدة
st.markdown("<h1 style='text-align: center; color: #38bdf8; font-weight: 800; font-size: 28px;'>⚡ صائد الموجات (نظام الحماية الذكي)</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 14px;'>مفعل بنجاح (RSI 70/30) فلتر التصحيح والتشبع للذهب</p>", unsafe_allow_html=True)

# تثبيت الإعدادات فنية للذهب وفريم 5 دقائق قسرياً في الخلفية لمنع التشتت
ticker = "GC=F" # رمز الذهب العالمي الموحد واللحظي
timeframe = "5m" # تثبيت الفريم على 5 دقائق لاقتناص أدق الفرص الحية

# جلب البيانات اللحظية الحية للذهب
@st.cache_data(ttl=10) # تحديث مستمر وثابت كل 10 ثوانٍ للسعر اللقيقي
def fetch_live_gold():
    df = yf.download(tickers=ticker, period="2d", interval=timeframe, progress=False)
    if not df.empty and isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    return df

df = fetch_live_gold()

if df.empty or len(df) < 20:
    st.markdown("<div class='box-hold'>🔄 جاري الاتصال بخادم أسعار الذهب ومزامنة فريم 5 دقائق الحقيقي...</div>", unsafe_allow_html=True)
else:
    # ------------------ محرك الاستراتيجية والمعادلات الرقمية ------------------
    # 1. حساب المتوسط المتحرك الأسي EMA 7
    df['EMA_7'] = df['Close'].ewm(span=7, adjust=False).mean()
    
    # 2. حساب مؤشر القوة النسبية RSI 14
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    rs = gain / (loss + 1e-10)
    df['RSI_14'] = 100 - (100 / (1 + rs))
    
    # 3. حساب السوبر تريند الحقيقي الرياضي الدقيق للذهب (ATR 10, Multiplier 3)
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

    # قراءة بيانات الشمعة اللحظية الحالية من فريم الـ 5 دقائق
    last_candle = df.iloc[-1]
    current_price = round(float(last_candle['Close']), 2)
    ema_val = round(float(last_candle['EMA_7']), 2)
    rsi_val = round(float(last_candle['RSI_14']), 2)
    st_dir = int(last_candle['ST_Dir'])
    st_line = round(float(last_candle['ST_Line']), 2)
    atr_val = float(last_candle['ATR'])
    
    # حساب المسافات السعرية للأهداف وفقاً لحركة ونقاط الذهب الحالية
    tp1_buy = round(current_price + (atr_val * 1.5), 2)
    tp2_buy = round(current_price + (atr_val * 3.0), 2)
    sl_buy = round(st_line, 2)
    
    tp1_sell = round(current_price - (atr_val * 1.5), 2)
    tp2_sell = round(current_price - (atr_val * 3.0), 2)
    sl_sell = round(st_line, 2)

    # تصفية وإصدار الإشارة الرقمية الصافية
    signal_status = "hold"
    if st_dir == 1:
        if current_price > ema_val and rsi_val < 70:
            signal_status = "buy"
    elif st_dir == -1:
        if current_price < ema_val and rsi_val > 30:
            signal_status = "sell"

    # ------------------ بناء الواجهة الرقمية الاحترافية كالصورة تماماً ------------------
    
    # 1. شريط الحالة العلوي البرتقالي النشط
    st.markdown("<div class='header-banner'>⚡ SMART CORRECTION & RSI FILTER ACTIVE</div>", unsafe_allow_html=True)
    
    # 2. مربع الفرصة الرئيسي الكبير
    if signal_status == "buy":
        st.markdown("<div class='box-buy'>🟢 فرصة شراء متاحة (تصحيح بسيط مقبول)</div>", unsafe_allow_html=True)
        st.markdown("<div class='condition-box'>🚀 شروط الاستراتيجية مكتملة (اقتنص الفرصة بلا تردد)</div>", unsafe_allow_html=True)
        play_sound()
    elif signal_status == "sell":
        st.markdown("<div class='box-sell'>🔴 فرصة بيع متاحة (استمرار زخم هابط)</div>", unsafe_allow_html=True)
        st.markdown("<div class='condition-box'>📉 شروط الاستراتيجية مكتملة بيعاً (اقتنص الفرصة)</div>", unsafe_allow_html=True)
        play_sound()
    else:
        st.markdown("<div class='box-hold'>⚪ وضع الانتظار والمراقبة مستمرة الآن على فريم 5 دقائق</div>", unsafe_allow_html=True)
        st.markdown("<div class='condition-box'>🔍 المحرك الآلي يراقب الأسعار... انتظر اكتمال الشروط بالكامل</div>", unsafe_allow_html=True)

    # 3. قسم كروت البيانات الأربعة (صفين متوازيين متناسقين للجوال)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"<div class='data-card'><div class='data-label'>السعر:</div><div class='data-value'>{current_price}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='data-card'><div class='data-label'>RSI 14:</div><div class='data-value'>{rsi_val}</div></div>", unsafe_allow_html=True)
    with col_b:
        st.markdown(f"<div class='data-card'><div class='data-label'>EMA 7:</div><div class='data-value'>{ema_val}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='data-card'><div class='data-label'>التريند:</div><div class='data-value'>{'صاعد' if st_dir == 1 else 'هابط'}</div></div>", unsafe_allow_html=True)

    st.write("")
    
    # 4. مستويات التنفيذ الرقمية الصافية (وقف الخسارة والأهداف) كالصورة
    st.markdown("<h4 style='text-align: center; color: #94a3b8; font-size: 15px;'>مستويات إدارة الصفقة المقترحة</h4>", unsafe_allow_html=True)
    col_sl, col_tp1, col_tp2 = st.columns(3)
    
    if st_dir == 1 or signal_status == "buy":
        with col_sl: st.markdown(f"<div class='target-sl'><p style='color:#64748b; font-size:12px; margin-bottom:2px;'>وقف الخسارة</p>{sl_buy}</div>", unsafe_allow_html=True)
