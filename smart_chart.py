import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
import time
import base64

# 1. إعدادات اللوحة الفنية الاحترافية المتقدمة
st.set_page_config(page_title="صائد الموجات الذكي Pro", page_icon="⚡", layout="wide")

# تصميم CSS فاخر يطابق المنصات العالمية ويعطي طابعاً داكناً مريحاً للعين
st.markdown("""
    <style>
    .stApp { background-color: #060913; color: #f8fafc; }
    .metric-card {
        background: linear-gradient(145deg, #0b132b, #1c2541);
        border: 1px solid #3a506b;
        border-radius: 12px; padding: 18px; text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.6);
    }
    .metric-title { color: #5bc0be; font-size: 13px; margin-bottom: 5px; font-weight: bold; }
    .metric-value { color: #ffffff; font-size: 24px; font-weight: 800; }
    
    .signal-buy {
        background: linear-gradient(90deg, #0f5132 0%, #082a1a 100%);
        border-left: 6px solid #198754; padding: 15px; border-radius: 8px; color: #75b798; font-weight: bold;
    }
    .signal-sell {
        background: linear-gradient(90deg, #842029 0%, #431014 100%);
        border-left: 6px solid #dc3545; padding: 15px; border-radius: 8px; color: #ea868f; font-weight: bold;
    }
    .signal-hold {
        background: #111827; border-left: 6px solid #6c757d; padding: 15px; border-radius: 8px; color: #adb5bd;
    }
    .box-sl { background-color: #dc3545; color: #fff; padding: 10px; border-radius: 6px; text-align: center; font-weight: bold; }
    .box-tp { background-color: #198754; color: #fff; padding: 10px; border-radius: 6px; text-align: center; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# دالة لتشغيل صوت تنبيه مخفي داخل المتصفح عند وجود فرصة
def play_sound():
    sound_html = """
    <iframe src="https://mixkit.co" allow="autoplay" style="display:none" id="iframeAudio"></iframe>
    """
    st.markdown(sound_html, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #00b4d8;'>⚡ نظام صائد الموجات المتكامل + شارت الشموع اليابانية</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>مراقبة الأسعار الحقيقية للمنصات ومطابقة الشارت والشموع لحظة بلحظة مع تنبيهات صوتية</p>", unsafe_allow_html=True)
st.write("---")

# 2. لوحة التحكم الجانبية واختيار السوق الموحد
st.sidebar.header("🎯 مراقبة الأسواق والمنصات")
market_type = st.sidebar.selectbox("اختر نوع السوق المُراد عرضه حالياً", ["عملات رقمية (Crypto)", "فوركس (Forex)", "أسهم وسلع (Stocks & Commodities)"])

if market_type == "فوركس (Forex)":
    assets = {"اليورو / دولار (EURUSD)": "EURUSD=X", "الباوند / دولار (GBPUSD)": "GBPUSD=X", "الدولار / ين (USDJPY)": "JPY=X"}
elif market_type == "عملات رقمية (Crypto)":
    assets = {"بيتكوين (BTCUSD)": "BTC-USD", "إيثيريوم (ETHUSD)": "ETH-USD", "سولانا (SOLUSD)": "SOL-USD"}
else:
    assets = {"الذهب (GOLD)": "GC=F", "نفط برنت (Crude Oil)": "BZ=F", "سهم تسلا (TSLA)": "TSLA"}

asset_label = st.sidebar.selectbox("اختر الأصل المالي لعرض الشارت والتحليل", list(assets.keys()))
ticker = assets[asset_label]
timeframe = st.sidebar.selectbox("الفريم الزمني للشمعة", ["5m", "15m", "1h", "4h", "1d"], index=2)
auto_refresh = st.sidebar.checkbox("تحديث الأسعار والشموع تلقائياً (كل 15 ثانية)", value=True)

# 3. جلب البيانات وتحليلها برمجياً لضمان مطابقة المنصة
@st.cache_data(ttl=15)
def fetch_live_data(symbol, tf):
    df = yf.download(tickers=symbol, period="5d", interval=tf, progress=False)
    if not df.empty and isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    return df

df = fetch_live_data(ticker, timeframe)

if df.empty or len(df) < 20:
    st.error("فشل الاتصال بمزود الأسعار اللحظية. تأكد من تفعيل الإنترنت أو غير الفريم السعري.")
else:
    # حساب المؤشرات الفنية بدقة المطابقة الفنية
    df['EMA_7'] = ta.ema(df['Close'], length=7)
    df['RSI_14'] = ta.rsi(df['Close'], length=14)
    st_ind = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
    
    df['ST_Dir'] = st_ind['SUPERTd_7_3.0']
    df['ST_Line'] = st_ind['SUPERT_7_3.0']
    
    # استخراج قيم آخر شمعة حية أغلقت في السوق
    last_candle = df.iloc[-1]
    current_price = round(float(last_candle['Close']), 4)
    ema_val = round(float(last_candle['EMA_7']), 4)
    rsi_val = round(float(last_candle['RSI_14']), 2)
    st_dir = int(last_candle['ST_Dir'])
    st_line = round(float(last_candle['ST_Line']), 4)
    
    # دالة ذكية لتحديد فرصة الدخول والأهداف بناءً على تذبذب الشموع
    risk = abs(current_price - st_line) if abs(current_price - st_line) > 0 else (current_price * 0.003)
    signal = "انتظار والمراقبة مستمرة ⏳"
    signal_type = "hold"
    tp1, tp2 = 0, 0
    
    if st_dir == 1:
        trend_text = "صاعد ⬆️"
        if current_price > ema_val and rsi_val < 70:
            signal = f"🟢 فرصة شراء متاحة الآن على {asset_label} - التصحيح مقبول والدخول آمن"
            signal_type = "buy"
            tp1 = round(current_price + (risk * 1.2), 4)
            tp2 = round(current_price + (risk * 2.2), 4)
            play_sound() # تشغيل جرس التنبيه
    else:
        trend_text = "هابط ⬇️"
        if current_price < ema_val and rsi_val > 30:
            signal = f"🔴 فرصة بيع (Short) متاحة الآن على {asset_label} - شروط الاتجاه مكتملة"
            signal_type = "sell"
            tp1 = round(current_price - (risk * 1.2), 4)
            tp2 = round(current_price - (risk * 2.2), 4)
            play_sound() # تشغيل جرس التنبيه

    # 4. عرض كروت المراقبة الرقمية الفورية
    st.markdown(f"### 📊 الحالة الفورية للأصل المالي: {asset_label}")
    
    if signal_type == "buy": st.markdown(f"<div class='signal-buy'>{signal}<br><span style='font-size:12px;'>شروط الاستراتيجية مكتملة (اقتنص الفرصة بلا تردد)</span></div>", unsafe_allow_html=True)
    elif signal_type == "sell": st.markdown(f"<div class='signal-sell'>{signal}<br><span style='font-size:12px;'>شروط الاستراتيجية مكتملة بيعاً (اقتنص الفرصة)</span></div>", unsafe_allow_html=True)
    else: st.markdown(f"<div class='signal-hold'>{signal}</div>", unsafe_allow_html=True)
    
    st.write("")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='metric-card'><div class='metric-title'>السعر اللحظي الحقيقي</div><div class='metric-value'>{current_price}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-card'><div class='metric-title'>خط المتوسط EMA 7</div><div class='metric-value'>{ema_val}</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-card'><div class='metric-title'>زخم القوة RSI 14</div><div class='metric-value'>{rsi_val}</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='metric-card'><div class='metric-title'>اتجاه السوبر تريند</div><div class='metric-value'>{trend_text}</div></div>", unsafe_allow_html=True)

    # 5. شاشة الشارت الفني المتقدم بالشموع اليابانية (Plotly Candlestick Chart)
    st.write("")
    st.markdown("### 📈 شارت الشموع اليابانية ومطابقة خطوط الاستراتيجية")
    
    # نأخذ آخر 40 شمعة فقط لجعل الشارت واضحاً واحترافياً على الجوال والكمبيوتر
    df_chart = df.tail(40)
    
    fig = go.Figure()
    
    # إضافة رسم الشموع اليابانية (أخضر للصعود وأحمر للهبوط)
    fig.add_trace(go.Candlestick(
        x=df_chart.index, open=df_chart['Open'], high=df_chart['High'], low=df_chart['Low'], close=df_chart['Close'],
        name='الشموع اليابانية', increasing_line_color='#10b981', decreasing_line_color='#ef4444'
    ))
    
    # إضافة خط المتوسط المتحرك EMA 7 فوق الشموع
    fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['EMA_7'], mode='lines', name='EMA 7', line=dict(color='#38bdf8', width=2)))
    
    # إضافة خط السوبر تريند الأوتوماتيكي لحماية الحساب وتحديد وقف الخسارة
    fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['ST_Line'], mode='lines', name='SuperTrend Line', line=dict(color='#eab308', width=2, dash='dash')))
    
    # تعديل مظهر وتصميم الشارت ليكون فخماً ومطابقاً للمنصات
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10), template="plotly_dark", paper_bgcolor="#060913", plot_bgcolor="#060913",
        xaxis_rangeslider_visible=False, yaxis=dict(gridcolor="#1e293b"), xaxis=dict(gridcolor="#1e293b"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # 6. إدارة الصفقات الرقمية المباشرة
    if signal_type in ["buy", "sell"]:
        st.markdown("### 🎯 مستويات التنفيذ وإدارة المخاطر المقترحة لحسابك")
        col_sl, col_tp1, col_tp2 = st.columns(3)
        with col_sl: st.markdown(f"<div class='box-sl'>🛑 وقف الخسارة الحقيقي (SL): {st_line}</div>", unsafe_allow_html=True)
        with col_tp1: st.markdown(f"<div class='box-tp'>🎯 الهدف الأول (TP1): {tp1}</div>", unsafe_allow_html=True)
        with col_tp2: st.markdown(f"<div class='box-tp'>🎯 الهدف الثاني (TP2): {tp2}</div>", unsafe_allow_html=True)

    # تشغيل آلية التحديث والمراقبة المستمرة للسعر الحقيقي
    if auto_refresh:
        time.sleep(15)
        st.rerun()
