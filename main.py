from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
import requests
import threading
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

class ScannerUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15

        self.status = Label(text="Status: Ready", color=(0, 1, 0, 1), font_size='16sp')
        self.symbol_label = Label(text="Symbol: BTC/USDT", font_size='18sp')
        
        self.signal_label = Label(text="Waiting for scan...", font_size='24sp', bold=True)
        self.price_label = Label(text="", font_size='18sp')
        self.risk_label = Label(text="", font_size='16sp', color=(0.8, 0.8, 0.8, 1))
        
        self.btn = Button(text="SCAN MARKET NOW", size_hint_y=None, height=80, background_color=(0.1, 0.5, 0.8, 1), font_size='18sp')
        self.btn.bind(on_press=self.scan_market)

        self.add_widget(self.status)
        self.add_widget(self.symbol_label)
        self.add_widget(self.signal_label)
        self.add_widget(self.price_label)
        self.add_widget(self.risk_label)
        self.add_widget(self.btn)

    def scan_market(self, instance):
        self.btn.disabled = True
        self.signal_label.text = "Analyzing..."
        self.signal_label.color = (1, 1, 1, 1)
        self.price_label.text = ""
        self.risk_label.text = "Calculating indicators..."
        self.status.text = "Status: Fetching Candles..."
        self.status.color = (1, 1, 0, 1)
        
        threading.Thread(target=self.run_scanner).start()

    def run_scanner(self):
        try:
            # آدرس API دریافت کندل‌ها
            url = "https://api.lbkex.com/v2/kline.do?symbol=btc_usdt&time=15min&size=100"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # بخش دیباگ: بررسی دقیق داده‌های دریافتی
            if "data" not in data:
                raise Exception(f"کلید data وجود ندارد. پاسخ سرور: {str(data)[:80]}")
            
            candles = data["data"]
            
            if not isinstance(candles, list):
                raise Exception(f"داده‌ها لیست نیستند. نوع داده: {type(candles)}")
                
            if len(candles) < 50:
                raise Exception(f"کندل کافی نیست. دریافت شده: {len(candles)} کندل")

            # استخراج قیمت‌ها
            closes = [float(c[4]) for c in candles]
            highs = [float(c[2]) for c in candles]
            lows = [float(c[3]) for c in candles]

            # محاسبه اندیکاتورها
            ema_9 = self.calc_ema(closes, 9)
            ema_21 = self.calc_ema(closes, 21)
            rsi = self.calc_rsi(closes, 14)
            atr = self.calc_atr(highs, lows, closes, 14)

            current_price = closes[-1]
            
            # موتور تصمیم‌گیری
            if ema_9[-1] > ema_21[-1] and 50 < rsi[-1] < 70:
                signal = "LONG 🟢"
                color = (0, 1, 0, 1)
                sl = current_price - (atr[-1] * 1.5)
                tp = current_price + (atr[-1] * 3.0)
            elif ema_9[-1] < ema_21[-1] and 30 < rsi[-1] < 50:
                signal = "SHORT 🔴"
                color = (1, 0, 0, 1)
                sl = current_price + (atr[-1] * 1.5)
                tp = current_price - (atr[-1] * 3.0)
            else:
                signal = "NEUTRAL ⚪"
                color = (0.7, 0.7, 0.7, 1)
                sl, tp = 0, 0

            # مدیریت ریسک
            account_balance = 1000
            risk_percent = 1.5
            risk_amount = account_balance * (risk_percent / 100)
            
            if signal != "NEUTRAL ⚪":
                position_size = risk_amount / abs(current_price - sl)
                risk_text = f"Risk: {risk_percent}% (${risk_amount:.2f})\nSize: {position_size:.4f} BTC\nSL: ${sl:.2f} | TP: ${tp:.2f}"
            else:
                risk_text = "No valid setup. Conditions not met."

            Clock.schedule_once(lambda dt: self.update_ui(signal, color, current_price, risk_text))

        except Exception as e:
            error_text = str(e)
            Clock.schedule_once(lambda dt: self.show_error(error_text))

    def calc_ema(self, prices, period):
        ema = [sum(prices[:period]) / period]
        multiplier = 2 / (period + 1)
        for price in prices[period:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        return [ema[0]] * (period - 1) + ema

    def calc_rsi(self, prices, period):
        gains, losses = [], []
        for i in range(1, len(prices)):
            diff = prices[i] - prices[i-1]
            gains.append(max(diff, 0))
            losses.append(max(-diff, 0))
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        rsi = []
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            rs = avg_gain / avg_loss if avg_loss != 0 else 100
            rsi.append(100 - (100 / (1 + rs)))
        return [50] * (period) + rsi

    def calc_atr(self, highs, lows, closes, period):
        trs = []
        for i in range(1, len(closes)):
            tr = max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1]))
            trs.append(tr)
        atr = [sum(trs[:period]) / period]
        for tr in trs[period:]:
            atr.append((atr[-1] * (period - 1) + tr) / period)
        return [atr[0]] * (period) + atr

    def update_ui(self, signal, color, price, risk_text):
        self.status.text = "Status: Scan Complete"
        self.status.color = (0, 1, 0, 1)
        self.signal_label.text = signal
        self.signal_label.color = color
        self.price_label.text = f"Entry Price: ${price:,.2f}"
        self.risk_label.text = risk_text
        self.btn.disabled = False

    def show_error(self, error_msg):
        self.status.text = "Status: Error"
        self.status.color = (1, 0, 0, 1)
        self.signal_label.text = "SCAN FAILED"
        # نمایش دقیق علت خطا
        self.price_label.text = error_msg
        self.risk_label.text = ""
        self.btn.disabled = False

class LBankScannerApp(App):
    def build(self):
        self.title = 'LBank Smart Scanner'
        return ScannerUI()

if __name__ == '__main__':
    LBankScannerApp().run()
