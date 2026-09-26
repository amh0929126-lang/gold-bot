import os
from flask import Flask
import pandas as pd
import numpy as np

app = Flask(__name__)

def advanced_wave_strategy():
    try:
        # شمعات متسلسلة لـ فريم 5 دقائق (محاكاة لموجة صاعدة تتخللها تصحيحات)
        data = {
            'High':  [2010, 2018, 2025, 2020, 2022, 2035, 2042, 2038, 2045],
            'Low':   [2000, 2008, 2012, 2008, 2015, 2022, 2030, 2028, 2036],
            'Close': [2005, 2015, 2022, 2010, 2020, 2032, 2040, 2032, 2044]
        }
        df = pd.DataFrame(data)

        # 1. حساب EMA 7 (المتوسط المتحرك الأسي 7)
        df['EMA_7'] = df['Close'].ewm(span=7, adjust=False).mean()

        # 2. حساب مؤشر RSI 14
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
        rs = gain / (loss + 1e-9)
        df['RSI_14'] = 100 - (100 / (1 + rs))

        # القيم الحالية والمجهزة للمقارنة
        last_close = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        last_ema = df['EMA_7'].iloc[-1]
        last_rsi = df['RSI_14'].iloc[-1]

        # كشف الاتجاه والتصحيح
        is_above_ema = last_close > last_ema
        is_rebound = last_close > prev_close  # التأكد من انتهاء التصحيح والارتداد

        signal = "⏳ جاري مسح الموجة..."
        status_class = "wait"
        advice = "انتظر الشمعة الحالية لتأكيد اتجاه الموجة."

        # --- منطق اقتناص الصفقات المتكررة طوال الموجة ---
        
        # 🟢 حالة 1: الموجه صاعدة + استكمال الدخول بعد التصحيح
        if is_above_ema:
            if is_rebound and 45 <= last_rsi <= 75:
                signal = "🟢 تجديد دخول شراء (BUY WAVE RE-ENTRY)"
                status_class = "buy"
                advice = "الموجة الصاعدة مستمرة وهناك ارتداد ممتازة بعد تصحيح. فرصة دخول جديدة الآن!"
            elif not is_rebound and last_rsi > 70:
                signal = "⚠️ تصحيح حاد مؤقت (لا تخرج، انتظر الارتداد)"
                status_class = "warning"
                advice = "السوق يصحح حالياً داخل الموجة الصاعدة. انتظر شمعة ارتداد حمراء إلى خضراء للدخول مجدداً."
            else:
                signal = "🟢 استمرار الاتجاه الصاعد (BUY)"
                status_class = "buy"
                advice = "الشروط متوفرة بالكامل للاستمرار مع الموجة."

        # 🔴 حالة 2: الموجه هابطة + استكمال الدخول بعد التصحيح الصاعد
        elif not is_above_ema:
            if not is_rebound and 25 <= last_rsi <= 55:
                signal = "🔴 تجديد دخول بيع (SELL WAVE RE-ENTRY)"
                status_class = "sell"
                advice = "الموجة الهابطة مستمرة والسعر يواصل الهبوط بعد تصحيح. فرصة بيع جديدة الآن!"
            elif is_rebound and last_rsi < 30:
                signal = "⚠️ تصحيح صاعد مؤقت (انتظر انتهاء الارتداد)"
                status_class = "warning"
                advice = "تصحيح صاعد مؤقت داخل الموجة الهابطة. انتظر استئناف الهبوط للدخول."
            else:
                signal = "🔴 استمرار الاتجاه الهابط (SELL)"
                status_class = "sell"
                advice = "الشروط متوفرة للاستمرار في صفقات البيع."

        return {
            "signal": signal,
            "class": status_class,
            "advice": advice,
            "close": last_close,
            "ema7": round(last_ema, 2),
            "rsi": round(last_rsi, 2)
        }
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def dashboard():
    res = advanced_wave_strategy()
    
    html = f"""
    <html>
        <head>
            <title>SuperTrend + EMA 7 + RSI 14 Wave Hunter</title>
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
                <h1>📊 صائد الموجات وتجديد الدخول الذكي</h1>
                <div class="sub-title">استراتيجية (SuperTrend + EMA 7 + RSI 14) - فريم 5 دقائق</div>
                
                <div class="signal-box {res.get('class')}">
                    {res.get('signal')}
                </div>

                <div class="advice">
                    💡 <b>توجيه الموجة اللحظي:</b> {res.get('advice')}
                </div>

                <div class="stats">
                    <div class="stat-item">السعر الحالي <b>{res.get('close')}</b></div>
                    <div class="stat-item">EMA 7 <b>{res.get('ema7')}</b></div>
                    <div class="stat-item">RSI 14 <b>{res.get('rsi')}</b></div>
                </div>
                
                <p style="color: #64748b; font-size: 11px; margin-top: 25px;">
                    قم بتحديث الصفحة مع كل شمعة 5 دقائق جديدة لاقتناص إعادة الدخول في الموجة وتفادي التصحيح الحاد.
                </p>
            </div>
        </body>
    </html>
    """
    return html

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
