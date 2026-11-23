
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

        self.orientation = "vertical"
        self.padding = 30
        self.spacing = 20

        self.status = Label(
            text="Status: Ready",
            color=(1, 1, 0, 1)
        )

        self.signal = Label(
            text="LBank Market Scanner\nReady",
            font_size="20sp",
            halign="center"
        )

        self.risk = Label(text="Risk: Not calculated")

        self.btn = Button(
            text="Check Market",
            size_hint_y=None,
            height=100
        )

        self.btn.bind(on_press=self.refresh)

        self.add_widget(self.status)
        self.add_widget(self.signal)
        self.add_widget(self.risk)
        self.add_widget(self.btn)

    def refresh(self, instance):
        self.btn.disabled = True
        self.signal.text = "Fetching live market data..."
        self.status.text = "Status: Connecting..."
        self.status.color = (1, 1, 0, 1)

        threading.Thread(
            target=self.get_lbank_data,
            daemon=True
        ).start()

    def get_lbank_data(self):

        try:
            url = "https://api.lbkex.com/v2/ticker/24hr.do"

            response = requests.get(
                url,
                params={"symbol": "btc_usdt"},
                timeout=15,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            response.raise_for_status()

            result = response.json()

            if not isinstance(result, dict):
                raise ValueError("Invalid API response")

            if str(result.get("result", "")).lower() != "true":
                raise ValueError(
                    "LBank API rejected request: " +
                    str(result.get("msg", "Unknown error"))
                )

            market_data = result.get("data")

            if isinstance(market_data, list):
                if not market_data:
                    raise ValueError("Empty market data")
                market_data = market_data[0]

            if not isinstance(market_data, dict):
                raise ValueError("Invalid market data structure")

            ticker = market_data.get("ticker", market_data)

            if not isinstance(ticker, dict):
                raise ValueError("Ticker format invalid")

            price = ticker.get("latest", ticker.get("last"))
            change = ticker.get("change")

            if price is None:
                raise ValueError("BTC price not found")

            price = float(price)

            if change is None:
                change_text = "Unavailable"
            else:
                change_text = str(change)

            Clock.schedule_once(
                lambda dt: self.update_success(
                    price, change_text
                )
            )

        except Exception as e:

            error = str(e)

            Clock.schedule_once(
                lambda dt: self.update_error(error)
            )

    def update_success(self, price, change):

        self.status.text = "Status: LIVE DATA"
        self.status.color = (0, 1, 0, 1)

        self.signal.text = (
            "BTC / USDT\n\n"
            f"Price: ${price:,.2f}\n"
            f"24h Change: {change}%"
        )

        self.risk.text = "Risk: Not calculated"

        self.btn.disabled = False

    def update_error(self, error):

        self.status.text = "Status: ERROR"
        self.status.color = (1, 0, 0, 1)

        self.signal.text = (
            "API ERROR\n\n" + error[:250]
        )

        self.btn.disabled = False


class LBankScannerApp(App):

    def build(self):
        self.title = "LBank Scanner"
        return ScannerUI()


if __name__ == "__main__":
    LBankScannerApp().run()
