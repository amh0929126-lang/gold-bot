import os
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    # القيم الافتراضية
    close = 4285.89
    ema7 = 4286.31
    rsi = 41.94
    
    signal = "⏳ بانتظار إدخال بيانات منصة Exness..."
    status_class = "wait"
    advice = "قم بإدخال قيم السعر، EMA 7، و RSI من منصة Exness الخاصة بك في الأسفل واضغط فحص الموجة."

    if request.method == 'POST':
        try:
            close = float(request.form.get('close', 4285.89))
            ema7 = float(request.form.get('ema7', 4286.31))
            rsi = float(request.form.get('rsi', 41.94))
            
            # حساب الحركة بناءً على القيم المدخلة
            is_above_ema = close > ema7
            # افترضنا افتراضاً بسيطاً للارتداد، أو يمكنك تعديل المنطق حسب رغبتك
            is_rebound = close >= ema7 

            # --- منطق صائد الموجات (Wave Hunter) ---
            if is_above_ema:
                if 45 <= rsi <= 75:
                    signal = "🟢 تجديد دخول شراء (BUY WAVE RE-ENTRY)"
                    status_class = "buy"
                    advice = "الموجة الصاعدة مستمرة وهناك ارتداد ممتاز بعد تصحيح. فرصة دخول شراء جديدة."
                elif rsi > 70:
                    signal = "⚠️ تصحيح حاد مؤقت (تشبع شراء)"
                    status_class = "warning"
                    advice = "السعر مرتفع وقريب من التشبع. انتظر تصحيحاً طفيفاً قبل الدخول."
                else:
                    signal = "🟢 استمرار الاتجاه الصاعد (BUY)"
                    status_class = "buy"
                    advice = "الشروط متوفرة للاستمرار مع الموجة الصاعدة."
            else:
                if 25 <= rsi <= 55:
                    signal = "🔴 تجديد دخول بيع (SELL WAVE RE-ENTRY)"
                    status_class = "sell"
                    advice = "الموجة الهابطة مستمرة وسعر يواصل الهبوط بعد تصحيح. فرصة دخول بيع جديدة."
                elif rsi < 30:
                    signal = "⚠️ تصحيح صاعد مؤقت (تشبع بيع)"
                    status_class = "warning"
                    advice = "السعر منخفض وقريب من التشبع. انتظر تصحيحاً صاعداً طفيفاً لاستئناف البيع."
                else:
                    signal = "🔴 استمرار الاتجاه الهابط (SELL)"
                    status_class = "sell"
                    advice = "الشروط متوفرة للاستمرار في صفقات البيع."
                    
        except ValueError:
            signal = "❌ خطأ في الإدخال"
            status_class = "warning"
            advice = "الرجاء التأكد من إدخال أرقام صحيحة."

    html = f"""
    <html>
        <head>
            <title>Exness Wave Hunter - صائد الموجات</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; margin: 0; padding: 15px; background-color: #0b0f19; color: #f1f5f9; }}
                .card {{ background: #1e293b; padding: 20px; border-radius: 16px; display: inline-block; box-shadow: 0 10px 25px rgba(0,0,0,0.6); width: 100%; max-width: 500px; margin-top: 10px; box-sizing: border-box; }}
                h1 {{ color: #38bdf8; font-size: 20px; margin-bottom: 5px; }}
                .sub-title {{ color: #94a3b8; font-size: 13px; margin-bottom: 15px; }}
                .signal-box {{ background: #0f172a; padding: 15px; border-radius: 12px; margin: 15px 0; font-size: 16px; font-weight: bold; border-right: 6px solid #64748b; text-align: center; }}
                .buy {{ border-right-color: #22c55e; color: #22c55e; }}
                .sell {{ border-right-color: #ef4444; color: #ef4444; }}
                .warning {{ border-right-color: #eab308; color: #eab308; }}
                .wait {{ border-right-color: #64748b; color: #cbd5e1; }}
                .advice {{ background: rgba(56, 189, 248, 0.08); border: 1px solid #38bdf8; padding: 10px; border-radius: 8px; margin-top: 15px; font-size: 12px; color: #7dd3fc; line-height: 1.4; text-align: right; }}
                form {{ margin-top: 20px; text-align: right; background: #0f172a; padding: 15px; border-radius: 12px; }}
                label {{ display: block; font-size: 13px; color: #94a3b8; margin-bottom: 5px; }}
                input {{ width: 100%; padding: 10px; margin-bottom: 12px; background: #1e293b; border: 1px solid #334155; color: #fff; border-radius: 8px; font-size: 16px; box-sizing: border-box; }}
                button {{ background: #38bdf8; color: #0b0f19; border: none; padding: 12px; width: 100%; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; }}
                button:hover {{ background: #0ea5e9; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>🌊 صائد الموجات (Exness M5)</h1>
                <div class="sub-title">إدخال مباشر مطابق لشارت منصتك</div>
                
                <div class="signal-box {status_class}">
                    {signal}
                </div>

                <div class="advice">
                    💡 <b>التوجيه اللحظي:</b> {advice}
                </div>

                <form method="POST">
                    <label>السعر الحالي من Exness:</label>
                    <input type="text" name="close" value="{close}" required>
                    
                    <label>قيمة EMA 7:</label>
                    <input type="text" name="ema7" value="{ema7}" required>
                    
                    <label>قيمة RSI 14:</label>
                    <input type="text" name="rsi" value="{rsi}" required>
                    
                    <button type="submit">فحص إشارة الموجة 🔍</button>
                </form>
            </div>
        </body>
    </html>
    """
    return html

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
