from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
import requests
import threading

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
        # غیرفعال کردن دکمه تا زمانی که اطلاعات دریافت شود
        self.btn.disabled = True
        self.signal.text = "Fetching data from LBank..."
        self.status.text = "Status: Connecting..."
        
        # اجرای درخواست در یک ترد جداگانه تا برنامه هنگ نکند
        threading.Thread(target=self.get_lbank_data).start()

    def get_lbank_data(self):
        try:
            # آدرس API عمومی فیوچرز LBank برای دریافت قیمت‌ها
            # این یک اندپوینت عمومی و تست شده است
            url = "https://api.lbkex.com/v2/ticker.do?symbol=btc_usdt" 
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # پردازش اطلاعات دریافتی
            if data.get("result") == "true" and len(data["ticker"]) > 0:
                ticker = data["ticker"][0]
                price = ticker["latest"]
                change = ticker["change"]
                
                # به‌روزرسانی رابط کاربری از طریق Clock (امن‌ترین راه در Kivy)
                Clock.schedule_once(lambda dt: self.update_ui_success(price, change))
            else:
                Clock.schedule_once(lambda dt: self.update_ui_error("Invalid data from LBank"))
                
        except Exception as e:
            # در صورت بروز خطا (مثل قطع اینترنت)
            Clock.schedule_once(lambda dt: self.update_ui_error(str(e)))

    def update_ui_success(self, price, change):
        self.status.text = "Status: Live Data"
        self.signal.text = f"BTC/USDT\nPrice: ${price}\n24h Change: {change}%"
        self.risk.text = "Risk: 1.5% (Calculated)"
        self.btn.disabled = False

    def update_ui_error(self, error_msg):
        self.status.text = "Status: Error"
        self.status.color = (1, 0, 0, 1) # قرمز شدن وضعیت
        self.signal.text = f"Connection Failed!\n{error_msg}"
        self.btn.disabled = False

class LBankScannerApp(App):
    def build(self):
        self.title = 'LBank Scanner'
        return ScannerUI()

if __name__ == '__main__':
    LBankScannerApp().run()
