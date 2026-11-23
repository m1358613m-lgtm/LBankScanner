# 1. ایمپورت‌ها در بالاترین خط
import requests
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
# ... بقیه ایمپورت‌های کوی (Kivy)

# 2. تابع دریافت کندل‌ها (بیرون از کلاس‌ها)
def get_lbank_candles(symbol="BTC/USDT", timeframe="15m", size=100):
    lbank_symbol = symbol.replace("/", "_").lower()
    timeframe_map = {
        "1m": "minute1", "3m": "minute3", "5m": "minute5", "15m": "minute15", "30m": "minute30",
        "1h": "hour1", "2h": "hour2", "4h": "hour4", "8h": "hour8", "12h": "hour12",
        "1d": "day1", "1w": "week1"
    }
    lbank_type = timeframe_map.get(timeframe.lower(), timeframe)

    try:
        size = int(size)
        size = min(max(size, 1), 2000)
    except:
        size = 100 

    url = "https://api.lbank.info/v2/kline.do"
    params = {
        "symbol": lbank_symbol,
        "type": lbank_type,
        "size": size,
        "time": int(time.time())
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if "data" not in data:
            print(f"خطای LBank: {data}")
            return None
        return data["data"]
    except Exception as e:
        print(f"خطا در اتصال به LBank: {e}")
        return None

# 3. کلاس اصلی برنامه شما
class LBankScannerApp(App):
    def build(self):
        # کدهای رابط کاربری شما (دکمه اسکن، لیبل‌ها و...)
        layout = BoxLayout(orientation='vertical')
        self.status_label = Label(text="Status: Ready")
        layout.add_widget(self.status_label)
        return layout
        
    def scan_market(self):
        # اینجا جایی است که تابع را صدا می‌زنید
        self.status_label.text = "Fetching Candles..."
        candles = get_lbank_candles(symbol="BTC/USDT", timeframe="15m")
        if candles:
            self.status_label.text = "Analyzing..."
        else:
            self.status_label.text = "Status: Error"

if __name__ == '__main__':
    LBankScannerApp().run()
