import requests
import time
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window

# تنظیم رنگ پس‌زمینه به مشکی (مثل تصاویر شما)
Window.clearcolor = (0, 0, 0, 1)

def get_lbank_candles(symbol="BTC/USDT", timeframe="15m", size=100):
    """
    دریافت کندل‌ها از LBank با اصلاح خودکار پارامترها
    """
    # 1. اصلاح فرمت نماد (مثلاً BTC/USDT به btc_usdt)
    lbank_symbol = symbol.replace("/", "_").lower()

    # 2. نگاشت تایم‌فریم به استاندارد LBank
    timeframe_map = {
        "1m": "minute1", "3m": "minute3", "5m": "minute5", "15m": "minute15", "30m": "minute30",
        "1h": "hour1", "2h": "hour2", "4h": "hour4", "8h": "hour8", "12h": "hour12",
        "1d": "day1", "1w": "week1"
    }
    lbank_type = timeframe_map.get(timeframe.lower(), timeframe)

    # 3. اطمینان از عدد صحیح بودن حجم و رعایت محدودیت LBank (1 تا 2000)
    try:
        size = int(size)
        size = min(max(size, 1), 2000)
    except:
        size = 100 

    # 4. ارسال درخواست به LBank
    url = "https://api.lbank.info/v2/kline.do"
    params = {
        "symbol": lbank_symbol,
        "type": lbank_type,
        "size": size,
        "time": int(time.time())
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # بررسی وجود کلید data در پاسخ
        if "data" not in data:
            return None, f"No 'data' key. Response: {data}"
            
        return data["data"], None
    except Exception as e:
        return None, str(e)

class LBankScannerApp(App):
    def build(self):
        # چیدمان اصلی
        self.layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        # لیبل وضعیت (بالای صفحه)
        self.status_label = Label(text="Status: Ready", color=(1, 1, 1, 1), font_size='20sp')
        
        # لیبل نماد
        self.symbol_label = Label(text="Symbol: BTC/USDT", color=(1, 1, 1, 1), font_size='20sp')
        
        # لیبل عملیات (Analyzing / SCAN FAILED)
        self.action_label = Label(text="", color=(1, 1, 1, 1), font_size='24sp', bold=True)
        
        # لیبل خطا
        self.error_label = Label(text="", color=(1, 0, 0, 1), font_size='14sp', 
                                 text_size=(Window.width - 80, None), halign='center', valign='middle')
        
        # اضافه کردن لیبل‌ها به صفحه
        self.layout.add_widget(self.status_label)
        self.layout.add_widget(self.symbol_label)
        self.layout.add_widget(self.action_label)
        self.layout.add_widget(self.error_label)
        
        # یک فضای خالی برای هل دادن دکمه به پایین صفحه
        self.layout.add_widget(Label())
        
        # دکمه اسکن (پایین صفحه)
        self.scan_btn = Button(text="SCAN MARKET NOW", size_hint_y=None, height=60, 
                               background_color=(0.1, 0.2, 0.3, 1), font_size='18sp')
        self.scan_btn.bind(on_press=self.start_scan)
        self.layout.add_widget(self.scan_btn)
        
        return self.layout

    def start_scan(self, instance):
        # اجرای عملیات در یک ترد (Thread) جداگانه تا برنامه هنگ نکند
        self.scan_btn.disabled = True # غیرفعال کردن دکمه هنگام اسکن
        threading.Thread(target=self.scan_market).start()

    def scan_market(self):
        # مرحله 1: وضعیت دریافت کندل (رنگ زرد)
        self.update_ui("Status: Fetching Candles...", "Connecting to LBank...", "", (1, 1, 0, 1))
        
        # فراخوانی تابع دریافت کندل
        candles, error = get_lbank_candles(symbol="BTC/USDT", timeframe="15m")
        
        if error:
            # مرحله خطا (رنگ قرمز)
            self.update_ui("Status: Error", "SCAN FAILED", error, (1, 0, 0, 1))
        else:
            # مرحله موفقیت (رنگ سبز)
            self.update_ui("Status: Success", "Analyzing...\nCalculating indicators (EMA, RSI, ATR)...", "", (0, 1, 0, 1))
            # در اینجا می‌توانید کدهای محاسبه اندیکاتورها را قرار دهید
            
        # فعال کردن مجدد دکمه
        Clock.schedule_once(lambda dt: setattr(self.scan_btn, 'disabled', False), 0)

    def update_ui(self, status, action, error, color):
        # استفاده از Clock برای آپدیت ایمن رابط کاربری از داخل ترد
        def update(dt):
            self.status_label.text = status
            self.status_label.color = color
            self.action_label.text = action
            self.error_label.text = error
        Clock.schedule_once(update, 0)

if __name__ == '__main__':
    LBankScannerApp().run()
