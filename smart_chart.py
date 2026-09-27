import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.graph_objects as go
import time

# 1. إعدادات اللوحة البريموم الفاخرة للذهب
st.set_page_config(page_title="رادار الذهب الذكي - فريم 5 دقائق", page_icon="🏆", layout="centered")

# تصميم CSS فخم جداً ومظلم يطابق المنصات الاحترافية العالمية
st.markdown("""
    <style>
    .stApp { background-color: #060913; color: #f8fafc; }
    
    /* شريط الحالة المطور */
    .header-banner {
        background: linear-gradient(90deg, #ff6b00 0%, #ff8c00 100%); color: #ffffff; padding: 12px; 
        border-radius: 8px; text-align: center; font-weight: bold; 
        font-size: 15px; box-shadow: 0 4px 10px rgba(255, 107, 0, 0.3); margin-bottom: 20px;
    }
    
    /* صناديق الدخول والتشبع الفوري */
    .box-buy-now {
        border: 2px solid #10b981; background: linear-gradient(90deg, rgba(16, 185, 129, 0.2) 0%, rgba(6, 78, 59, 0.4) 100%);
        border-radius: 12px; padding: 20px; text-align: center; color: #34d399; font-size: 22px; font-weight: 800;
    }
    .box-sell-now {
        border: 2px solid #ef4444; background: linear-gradient(90deg, rgba(239, 68, 68, 0.2) 0%, rgba(69, 10, 10, 0.4) 100%);
        border-radius: 12px; padding: 20px; text-align: center; color: #f87171; font-size: 22px; font-weight: 800;
    }
    .box-hold-wait {
        border: 1px dashed #64748b; background-color: #0f172a;
        border-radius: 12px; padding: 20px; text-align: center; color: #94a3b8; font-size: 18px;
    }
    
    .condition-sub {
        background-color: #1e293b; border-radius: 6px; padding: 8px; margin-top: 10px;
        font-size: 13px; color: #38bdf8; font-weight: bold;
    }
    
    /* كروت عرض البيانات الفنية */
    .data-card {
        background-color: #0f172a; border: 1px solid #1e293b;
        border-radius: 10px; padding: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .data-label { color: #64748b; font-size: 13px; font-weight: bold; }
    .data-value { color: #ffffff; font-size: 22px; font-weight: bold; margin-top: 5px; }
    
    /* أرقام الصفقات */
    .target-sl { color: #f87171; font-size: 18px; font-weight: bold; text-align: center; background:#450a0a; padding: 10px; border-radius:6px;}
    .target-tp { color: #4ade80; font-size: 18px; font-weight: bold; text-align: center; background:#022c22; padding: 10px; border-radius:6px;}
    
    .info-box {
        border: 1px solid #334155; background-color: #0f172a;
        border-radius: 10px; padding: 15px; font-size: 14px; line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

def play_sound():
    sound_html = '<iframe src="https://mixkit.co" allow="autoplay" style="display:none" id="iframeAudio"></iframe>'
    st.markdown(sound_html, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #d4af37; font-weight: 800;'>🏆 رادار الذهب ومقتنص صفقات السعر الفوري</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 14px;'>تحليل متقدم للتصحيحات ومستويات التشبع (RSI 70/30) • فريم 5 دقائق</p>", unsafe_allow_html=True)

# تثبيت الرمز الفوري الدقيق والمطابق لمنصة Exness 100%
ticker = "XAUUSD=X"
timeframe = "5m"

@st.cache_data(ttl=5)
def fetch_live_gold():
    df = yf.download(tickers=ticker, period="1d", interval=timeframe, progress=False)
    if not df.empty and isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    return df

df = fetch_live_gold()

if df.empty or len(df) < 15:
    st.markdown("<div class='box-hold-wait'>🔄 جاري مزامنة النبضات السعرية والمؤشرات الفنية للذهب...</div>", unsafe_allow_html=True)
else:
    # ------------------ المحرك الرياضي الدقيق للمؤشرات ------------------
    df['EMA_7'] = df['Close'].ewm(span=7, adjust=False).mean()
    
    # حساب RSI 14 بدقة البورصة
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    rs = gain / (loss + 1e-10)
    df['RSI_14'] = 100 - (100 / (1 + rs))
    
    # حساب السوبر تريند (ATR 10, Multiplier 3)
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

    last_candle = df.iloc[-1]
    current_price = round(float(last_candle['Close']), 2)
    ema_val = round(float(last_candle['EMA_7']), 2)
    rsi_val = round(float(last_candle['RSI_14']), 2)
    st_dir = int(last_candle['ST_Dir'])
    st_line = round(float(last_candle['ST_Line']), 2)
    atr_val = float(last_candle['ATR'])

    # ------------------ محرك الفرز الذكي لتحديد زمن الدخول بدقة ------------------
    entry_timing = "انتظار واقتناص الإشارة المعيارية الحية ⏳"
    signal_status = "hold"
    guidance = "السوق الآن في مرحلة توازن. المحرك يراقب ارتداد السعر من مستويات الدعم والمقاومة لخط السوبر تريند الحقيقي لتوليد فرصة دخول آمنة."
    
    if st_dir == 1: # الاتجاه العام صاعد
        if current_price > ema_val:
            if rsi_val >= 70:
                signal_status = "hold_buy"
                entry_timing = "⚠️ تجميد الدخول (السوق وصل للتشبع الشرائي في القمة)"
                guidance = "الذهب صاعد ولكن مؤشر RSI تخطى 70 في القمة. لا تشتري الآن لتتجنب الانعكاس المؤقت، انتظر حتى يهبط السعر لتصحيح بسيط."
            elif rsi_val <= 35:
                signal_status = "buy_now"
                entry_timing = "🔥 فرصة ذهبية للدخول (انتهاء التصحيح والارتداد من القاع)"
                guidance = "الذهب في اتجاه صاعد عام ووصل لمستويات تصحيح عميقة وقريبة من ذروة البيع. الدخول شراء الآن يعتبر نموذجياً وبأقل نسبة مخاطرة."
            else:
                signal_status = "buy_now"
                entry_timing = "🟢 اقتنص صفقة الشراء الآن (موجة صاعدة مستقرة)"
                guidance = "الاتجاه صاعد والسعر مستقر فوق متوسط EMA 7 وزخم RSI متوازن. الدخول شراء مناسب ومستمر نحو الأهداف."
    else: # الاتجاه العام هابط
        if current_price < ema_val:
            if rsi_val <= 30:
                signal_status = "hold_sell"
                entry_timing = "⚠️ تجميد الدخول (السوق وصل للتشبع البيعي في القاع)"
                guidance = "الاتجاه هابط ولكن الذهب غرق في ذروة البيع (RSI تحت 30). قد يحدث ارتداد صعودي تصحيحي في أي لحظة، انتظر صعود السعر قليلاً لتبيع من قمة أفضل."
            elif rsi_val >= 65:
                signal_status = "sell_now"
                entry_timing = "🔥 فرصة ذهبية للبيع (انتهاء التصحيح الصعودي المؤقت)"
                guidance = "الاتجاه العام هابط والذهب قام بتصحيح صعودي مؤقت ووصل لتشبع شرائي نسبي. هذا هو الوقت المثالي لفتح صفقة بيع (Short) من القمة."
            else:
                signal_status = "sell_now"
                entry_timing = "🔴 اقتنص صفقة البيع الآن (زخم هابط قوي)"
                guidance = "الاتجاه هابط والذهب يواصل النزيف تحت خطوط المقاومة وخط EMA 7 بشكل مستقر وسلس. الدخول بيع يواكب الموجة الحالية."

    # حساب مستويات الأهداف الدقيقة المفلترة بالتذبذب اللحظي لحساب إكسنس
    tp1_buy = round(current_price + (atr_val * 1.5), 2)
    tp2_buy = round(current_price + (atr_val * 3.0), 2)
    sl_buy = round(st_line, 2)
    
    tp1_sell = round(current_price - (atr_val * 1.5), 2)
    tp2_sell = round(current_price - (atr_val * 3.0), 2)
    sl_sell = round(st_line, 2)

    # ------------------ بناء وتحديث الواجهة الاحترافية ------------------
    st.markdown("<div class='header-banner'>⚡ SMART TIMING FILTER & GOLD TREND SCANNER ACTIVE</div>", unsafe_allow_html=True)
    
    # عرض صندوق الحالة والزمن المناسب للدخول كعنوان رئيسي ملون
    if "buy_now" in signal_status:
        st.markdown(f"<div class='box-buy-now'>{entry_timing}</div>", unsafe_allow_html=True)
        st.markdown("<div class='condition-box'>🚀 شروط الاستراتيجية متوافقة بالكامل للذهب (دخول آمن فوراً)</div>", unsafe_allow_html=True)
        play_sound()
    elif "sell_now" in signal_status:
        st.markdown(f"<div class='box-sell-now'>{entry_timing}</div>", unsafe_allow_html=True)
        st.markdown("<div class='condition-box'>📉 شروط الاتجاه مكتملة لركوب الموجة الهابطة (بيع فوري)</div>", unsafe_allow_html=True)
        play_sound()
    else:
        st.markdown(f"<div class='box-hold-wait'>⚪ {entry_timing}</div>", unsafe_allow_html=True)
