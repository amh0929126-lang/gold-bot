import os
from flask import Flask
import pandas as pd
import yfinance as yf

app = Flask(__name__)

def get_live_wave_strategy():
    try:
        # جلب بيانات الذهب الحية من السوق (فريم 5 دقائق)
        ticker = "GC=F"  # أو استخدام "XAUUSD=X" لعقود الذهب الفورية
        df = yf.download(ticker, period="5d", interval="5m", progress=False)
        
        if df.empty:
            # محاولة بديلة لرمز الذهب في حال لم تتوافر البيانات
            ticker = "XAUUSD=X"
            df = yf.download(ticker, period="5d", interval="5m", progress=False)

        if df.empty:
            return {"error": "تعذر جلب بيانات السوق حالياً (السوق مغلق)." }

        # تنظيف وتح تجهيز البيانات
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)

        # 1. حساب EMA 7 (المتوسط المتحرك الأسي 7)
        df['EMA_7'] = df['Close'].ewm(span=7, adjust=False).mean()

        # 2. حساب مؤشر RSI 14
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
        rs = gain / (loss + 1e-9)
        df['RSI_14'] = 100 - (100 / (1 + rs))

        # القيم الأخيرة للسوق الحقيقي
        last_close = float(df['Close'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2])
        last_ema = float(df['EMA_7'].iloc[-1])
        last_rsi = float(df['RSI_14'].iloc[-1])

        is_above_ema = last_close > last_ema
        is_rebound = last_close > prev_close

        signal = "⏳ جاري مسح الموجة الحية..."
        status_class = "wait"
        advice = "انتظر الشمعة الحالية لتأكيد اتجاه الموجة من السوق المباشر."

        # --- منطق صائد الموجات الحقيقي ---
        if is_above_ema:
            if is_rebound and 45 <= last_rsi <= 75:
                signal = "🟢 تجديد دخول شراء (BUY WAVE RE-ENTRY)"
                status_class = "buy"
                advice = "الموجة الصاعدة حية ومستمرة وهناك ارتداد ممتاز بعد تصحيح."
            elif not is_rebound and last_rsi > 70:
                signal = "⚠️ تصحيح حاد مؤقت (انتظر الارتداد)"
                status_class = "warning"
                advice = "السوق يصحح حالياً داخل الموجة الصاعدة. انتظر شمعة ارتداد."
            else:
                signal = "🟢 استمرار الاتجاه الصاعد (BUY)"
                status_class = "buy"
                advice = "الشروط الحية متوفرة للاستمرار مع الموجة الصاعدة."
        else:
            if not is_rebound and 25 <= last_rsi <= 55:
                signal = "🔴 تجديد دخول بيع (SELL WAVE RE-ENTRY)"
                status_class = "sell"
                advice = "الموجة الهابطة حية ومستمرة والسعر يواصل الهبوط بعد تصحيح."
            elif is_rebound and last_rsi < 30:
                signal = "⚠️ تصحيح صاعد مؤقت (انتظر استئناف الهبوط)"
                status_class = "warning"
                advice = "تصحيح صاعد مؤقت داخل الموجة الهابطة الحية."
            else:
                signal = "🔴 استمرار الاتجاه الهابط (SELL)"
                status_class = "sell"
                advice = "الشروط الحية متوفرة للاستمرار في صفقات البيع."

        return {
            "signal": signal,
            "class": status_class,
            "advice": advice,
            "close": round(last_close, 2),
            "ema7": round(last_ema, 2),
            "rsi": round(last_rsi, 2)
        }
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def dashboard():
    res = get_live_wave_strategy()
    
    if "error" in res:
        error_msg = res["error"]
        return f"""
        <html>
            <head><meta charset="utf-8"><title>Gold Bot</title></head>
            <body style="background:#0b0f19; color:#f1f5f9; text-align:center; font-family:sans-serif; padding:50px;">
                <h2>⚠️ تنبيه من السوق</h2>
                <p>{error_msg}</p>
                <p style="color:#94a3b8;">السوق مغلق حالياً، ستعمل البيانات الحية تلقائياً فور افتتاحه يوم الإثنين.</p>
            </body>
        </html>
        """

    html = f"""
    <html>
        <head>
            <title>SuperTrend + EMA 7 + RSI 14 Live Wave Hunter</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; margin: 0; padding: 20px; background-color: #0b0f19; color: #f1f5f9; }}
                .card {{ background: #1e293b; padding: 30px; border-radius: 16px; display: inline-block; box-shadow: 0 10px 25px rgba(0,0,0,0.6); width: 90%; max-width: 600px; margin-top: 20px; }}
                h1 {{ color: #38bdf8; font-size: 22px; margin-bottom: 5px; }}
                .sub-title {{ color: #94a3b8; font-size: 14px; margin-bottom: 20px; }}
                .signal-box {{ background: #0f172a; padding: 20px; border-radius: 12px; margin: 20px 0; font-size: 18px; font-weight: bold; border-right: 6px solid #64748b; }}
                .buy {{ border-right-color: #22c55e; color: #22c55e; }}
                .sell {{ border-right-color: #ef4444; color: #ef4444; }}
                .warning {{ border-right-color: #eab308; color: #eab308; }}
                .wait {{ border-right-color: #64748b; color: #cbd5e1; }}
                .stats {{ display: flex; justify-content: space-around; background: #0f172a; padding: 15px; border-radius: 8px; margin-top: 15px; }}
                .stat-item {{ font-size: 13px; color: #94a3b8; }}
                .stat-item b {{ display: block; color: #f8fafc; font-size: 16px; margin-top: 5px; }}
                .advice {{ background: rgba(56, 189, 248, 0.08); border: 1px solid #38bdf8; padding: 12px; border-radius: 8px; margin-top: 15px; font-size: 13px; color: #7dd3fc; line-height: 1.5; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>📊 صائد الموجات الحقيقي (Live Gold)</h1>
                <div class="sub-title">استراتيجية (SuperTrend + EMA 7 + RSI 14) - فريم 5 دقائق</div>
                
                <div class="signal-box {res.get('class')}">
                    {res.get('signal')}
                </div>

                <div class="advice">
                    💡 <b>توجيه الموجة الحية:</b> {res.get('advice')}
                </div>

                <div class="stats">
                    <div class="stat-item">السعر الحي <b>{res.get('close')}</b></div>
                    <div class="stat-item">EMA 7 <b>{res.get('ema7')}</b></div>
                    <div class="stat-item">RSI 14 <b>{res.get('rsi')}</b></div>
                </div>
                
                <p style="color: #64748b; font-size: 11px; margin-top: 25px;">
                    يقوم هذا الإصدار بجلب بيانات الذهب الحية من السوق مباشرة.
                </p>
            </div>
        </body>
    </html>
    """
    return html

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
