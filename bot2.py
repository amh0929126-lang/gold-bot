import os
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    close = 4285.89
    ema7 = 4286.31
    rsi = 41.94
    super_trend = "صاعد"
    
    signal = "⏳ بانتظار إدخال بيانات منصة Exness..."
    status_class = "wait"
    advice = "قم بإدخال بيانات الشمعة الحالية من Exness لحساب الإشارة والأهداف بدقة."
    confidence = "مرتقب"
    conf_class = "wait"
    
    tp1, tp2, sl = 0.0, 0.0, 0.0

    if request.method == 'POST':
        try:
            close = float(request.form.get('close', 4285.89))
            ema7 = float(request.form.get('ema7', 4286.31))
            rsi = float(request.form.get('rsi', 41.94))
            super_trend = request.form.get('super_trend', 'صاعد')
            
            is_bullish_trend = (super_trend == 'صاعد')
            is_above_ema = close >= ema7

            if is_bullish_trend:
                sl = round(close - 3.5, 2)
                tp1 = round(close + 4.0, 2)
                tp2 = round(close + 8.0, 2)
                
                if is_above_ema and 45 <= rsi <= 75:
                    signal = "🟢 تجديد دخول شراء (BUY WAVE RE-ENTRY)"
                    status_class = "buy"
                    confidence = "🚀 دخول آمن ومؤكد 100% (نفذ بلا تردد)"
                    conf_class = "buy"
                    advice = "الشروط الفنية متوافقة تماماً. الموجة صاعدة وأنت تدخل مع الارتداد الصحيح."
                elif rsi > 70:
                    signal = "⚠️ تشبع شراء (لا تدخل الآن)"
                    status_class = "warning"
                    confidence = "🛑 تجنب الدخول (منطقة مخاطرة)"
                    conf_class = "warning"
                    advice = "الخوف هنا غير مبرر، لكن التسرع خطأ. انتظر هدوء السعر وتصحيحه نحو EMA 7."
                else:
                    signal = "🟢 استمرار الاتجاه الصاعد (BUY)"
                    status_class = "buy"
                    confidence = "✅ الدخول مستقر ومتاح"
                    conf_class = "buy"
                    advice = "الاتجاه العام صاعد، حافظ على هدوئك وتابع أهدافك المحددة."
            else:
                sl = round(close + 3.5, 2)
                tp1 = round(close - 4.0, 2)
                tp2 = round(close - 8.0, 2)
                
                if not is_above_ema and 25 <= rsi <= 55:
                    signal = "🔴 تجديد دخول بيع (SELL WAVE RE-ENTRY)"
                    status_class = "sell"
                    confidence = "🚀 دخول بيع آمن ومؤكد (نفذ بلا خوف)"
                    conf_class = "sell"
                    advice = "الفرصة مثالية لاستئناف الهبوط بعد التصحيح. توكل على الله ونفذ."
                elif rsi < 30:
                    signal = "⚠️ تشبع بيع (لا تبيع في القاع)"
                    status_class = "warning"
                    confidence = "🛑 خطر البيع المتأخر"
                    conf_class = "warning"
                    advice = "الأسعار قرب التشبع السفلي، البيع الآن قد يعرضك لارتداد عكسي مؤلم. انتظر."
                else:
                    signal = "🔴 استمرار الاتجاه الهابط (SELL)"
                    status_class = "sell"
                    confidence = "✅ الدخول الهابط مستقر"
                    conf_class = "sell"
                    advice = "الاتجاه هابط وثابت، الالتزام بالخطة يزيل تماماً أي شعور بالخوف."
                    
        except ValueError:
            signal = "❌ خطأ في الإدخال"
            status_class = "warning"
            confidence = "خطأ في قراءة الأرقام"
            conf_class = "warning"
            advice = "الرجاء التأكد من إدخال أرقام صحيحة."

    html = f"""
    <html>
        <head>
            <title>Exness Wave Hunter Master - صائد الموجات</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; margin: 0; padding: 15px; background-color: #0b0f19; color: #f1f5f9; }}
                .card {{ background: #1e293b; padding: 20px; border-radius: 16px; display: inline-block; box-shadow: 0 10px 25px rgba(0,0,0,0.6); width: 100%; max-width: 500px; margin-top: 10px; box-sizing: border-box; }}
                h1 {{ color: #38bdf8; font-size: 20px; margin-bottom: 5px; }}
                .sub-title {{ color: #94a3b8; font-size: 13px; margin-bottom: 15px; }}
                .signal-box {{ background: #0f172a; padding: 15px; border-radius: 12px; margin: 12px 0; font-size: 15px; font-weight: bold; border-right: 6px solid #64748b; text-align: center; }}
                .confidence-box {{ background: #0f172a; padding: 12px; border-radius: 12px; margin: 10px 0; font-size: 14px; font-weight: bold; text-align: center; border: 1px dashed #38bdf8; }}
                .buy {{ border-right-color: #22c55e; color: #22c55e; }}
                .sell {{ border-right-color: #ef4444; color: #ef4444; }}
                .warning {{ border-right-color: #eab308; color: #eab308; }}
                .wait {{ border-right-color: #64748b; color: #cbd5e1; }}
                .targets-box {{ display: flex; justify-content: space-between; background: #0f172a; padding: 12px; border-radius: 10px; margin-top: 12px; text-align: center; }}
                .target-item {{ font-size: 12px; color: #94a3b8; flex: 1; }}
                .target-item b {{ display: block; font-size: 15px; margin-top: 4px; }}
                .tp {{ color: #22c55e; }}
                .sl {{ color: #ef4444; }}
                .advice {{ background: rgba(56, 189, 248, 0.08); border: 1px solid #38bdf8; padding: 10px; border-radius: 8px; margin-top: 12px; font-size: 12px; color: #7dd3fc; line-height: 1.4; text-align: right; }}
                form {{ margin-top: 15px; text-align: right; background: #0f172a; padding: 15px; border-radius: 12px; }}
                label {{ display: block; font-size: 13px; color: #94a3b8; margin-bottom: 5px; }}
                input, select {{ width: 100%; padding: 10px; margin-bottom: 12px; background: #1e293b; border: 1px solid #334155; color: #fff; border-radius: 8px; font-size: 16px; box-sizing: border-box; }}
                button {{ background: #38bdf8; color: #0b0f19; border: none; padding: 12px; width: 100%; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; }}
                button:hover {{ background: #0ea5e9; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>🌊 صائد الموجات Master (Exness M5)</h1>
                <div class="sub-title">تحليل فني + فلتر الثقة ونزع التردد والخوف</div>
                
                <div class="signal-box {status_class}">
                    {signal}
                </div>

                <div class="confidence-box {conf_class}">
                    {confidence}
                </div>

                <div class="targets-box">
                    <div class="target-item sl">وقف الخسارة <b>{sl}</b></div>
                    <div class="target-item tp">الهدف 1 <b>{tp1}</b></div>
                    <div class="target-item tp">الهدف 2 <b>{tp2}</b></div>
                </div>

                <div class="advice">
                    💡 <b>التوجيه النفسي والفني:</b> {advice}
                </div>

                <form method="POST">
                    <label>حالة مؤشر السوبر تريند:</label>
                    <select name="super_trend">
                        <option value="صاعد" {"selected" if super_trend == "صاعد" else ""}>🟢 صاعد (Bullish)</option>
                        <option value="هابط" {"selected" if super_trend == "هابط" else ""}>🔴 هابط (Bearish)</option>
                    </select>

                    <label>السعر الحالي من Exness:</label>
                    <input type="text" name="close" value="{close}" required>
                    
                    <label>قيمة EMA 7:</label>
                    <input type="text" name="ema7" value="{ema7}" required>
                    
                    <label>قيمة RSI 14:</label>
                    <input type="text" name="rsi" value="{rsi}" required>
                    
                    <button type="submit">فحص الثقة وتحديد الصفقة 🎯</button>
                </form>
            </div>
        </body>
    </html>
    """
    return html

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
