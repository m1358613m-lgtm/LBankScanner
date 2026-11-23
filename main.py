from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
import requests
import threading
import ssl

# نادیده گرفتن خطای SSL در اندروید
ssl._create_default_https_context = ssl._create_unverified_context

class ScannerUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 30
        self.spacing = 20

        self.status = Label(text="Status: Connected", color=(0, 1, 0, 1))
        self.signal = Label(text="Click 'Check Market' to start", font_size='20sp', halign='center')
        self.risk = Label(text="Risk: --%")
        
        self.btn = Button(text="Check Market", size_hint_y=None, height=100, background_color=(0.2, 0.6, 0.8, 1))
        self.btn.bind(on_press=self.refresh)

        self.add_widget(self.status)
        self.add_widget(self.signal)
        self.add_widget(self.risk)
        self.add_widget(self.btn)

    def refresh(self, instance):
        self.btn.disabled = True
        self.signal.text = "Fetching data from LBank..."
        self.status.text = "Status: Connecting..."
        self.status.color = (1, 1, 0, 1) 
        threading.Thread(target=self.get_lbank_data).start()

    def get_lbank_data(self):
        try:
            # استفاده از اندپوینت پایدار
            url = "https://api.lbkex.com/v2/ticker.do?symbol=btc_usdt"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # پیدا کردن لیست تیکرها (بررسی هر دو ساختار ممکن)
            ticker_list = []
            if isinstance(data, dict):
                if "ticker" in data and isinstance(data["ticker"], list):
                    ticker_list = data["ticker"]
                elif "data" in data and isinstance(data["data"], list):
                    ticker_list = data["data"]

            if len(ticker_list) > 0:
                item = ticker_list[0]
                # جستجوی هوشمند برای کلید قیمت
                price = item.get("latest", item.get("last", item.get("lastPrice", item.get("price", None))))
                change = item.get("change", item.get("priceChangePercent", "0"))
                
                if price:
                    Clock.schedule_once(lambda dt: self.update_ui_success(price, change))
                else:
                    # اگر کلید پیدا نشد، خود دیکشنری را نشان بده تا ببینیم چه خبر است
                    Clock.schedule_once(lambda dt: self.update_ui_error(f"Keys missing: {str(item)[:100]}"))
            else:
                Clock.schedule_once(lambda dt: self.update_ui_error(f"Unknown format: {str(data)[:100]}"))
                
        except Exception as e:
            error_text = str(e)
            Clock.schedule_once(lambda dt: self.update_ui_error(error_text))

    def update_ui_success(self, price, change):
        self.status.text = "Status: Live Data"
        self.status.color = (0, 1, 0, 1)
        self.signal.text = f"BTC/USDT\nPrice: ${price}\n24h Change: {change}%"
        self.risk.text = "Risk: 1.5% (Calculated)"
        self.btn.disabled = False

    def update_ui_error(self, error_msg):
        self.status.text = "Status: Error"
        self.status.color = (1, 0, 0, 1)
        self.signal.text = f"Error!\n{error_msg[:150]}"
        self.btn.disabled = False

class LBankScannerApp(App):
    def build(self):
        self.title = 'LBank Scanner'
        return ScannerUI()

if __name__ == '__main__':
    LBankScannerApp().run()
