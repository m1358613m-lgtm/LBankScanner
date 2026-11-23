
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
import requests
import threading

BASE = "https://lbkperp.lbank.com/cfd/openApi/v1/pub"

class ScannerUI(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 25
        self.spacing = 15

        self.status = Label(
            text="Status: READY",
            color=(1, 1, 0, 1),
            font_size="18sp"
        )

        self.signal = Label(
            text="LBANK FUTURES SCANNER\n\nPress Check Market",
            font_size="19sp",
            halign="center"
        )

        self.details = Label(
            text="Contracts: --\nBTCUSDT: --"
        )

        self.risk = Label(text="Trading signals: Not active")

        self.btn = Button(
            text="Check Futures Market",
            size_hint_y=None,
            height=85
        )
        self.btn.bind(on_press=self.refresh)

        self.add_widget(self.status)
        self.add_widget(self.signal)
        self.add_widget(self.details)
        self.add_widget(self.risk)
        self.add_widget(self.btn)

    def refresh(self, instance):
        self.btn.disabled = True
        self.status.text = "Status: CONNECTING FUTURES..."
        self.signal.text = "Downloading contracts and prices..."
        self.details.text = "Please wait..."

        threading.Thread(
            target=self.get_futures,
            daemon=True
        ).start()

    def request_api(self, endpoint):

        response = requests.get(
            BASE + endpoint,
            params={"productGroup": "SwapU"},
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        response.raise_for_status()
        result = response.json()

        if not isinstance(result, dict):
            raise ValueError("Invalid API response")

        if str(result.get("result", "")).lower() != "true":
            raise ValueError(
                "API error: " + str(result.get("msg", result))
            )

        if result.get("error_code", 0) not in (0, "0", None):
            raise ValueError(
                "API code: " + str(result["error_code"])
            )

        return result

    def get_futures(self):

        try:
            # 1. Get futures contracts
            instruments = self.request_api(
                "/instrument"
            )

            contracts = instruments.get("data", [])

            if not isinstance(contracts, list):
                raise ValueError("Invalid contracts list")

            usdt_contracts = [
                item for item in contracts
                if isinstance(item, dict)
                and str(item.get("symbol", "")).upper().endswith("USDT")
                and str(item.get("clearCurrency", "")).upper() == "USDT"
            ]

            if not usdt_contracts:
                raise ValueError("No USDT futures contracts found")

            # 2. Get futures market prices
            markets = self.request_api(
                "/marketData"
            )

            tickers = markets.get("data", [])

            if not isinstance(tickers, list):
                raise ValueError("Invalid futures ticker list")

            if not tickers:
                raise ValueError("Empty futures market data")

            # 3. Find BTCUSDT
            btc = next(
                (
                    item for item in tickers
                    if isinstance(item, dict)
                    and item.get("symbol", "").upper() == "BTCUSDT"
                ),
                None
            )

            if btc is None:
                raise ValueError("BTCUSDT futures ticker not found")

            price = btc.get("lastPrice")
            mark = btc.get("markedPrice")
            volume = btc.get("volume")
            turnover = btc.get("turnover")

            if price is None or float(price) <= 0:
                raise ValueError("Invalid BTC futures price")

            # 4. Rank contracts by turnover
            ranked = sorted(
                [
                    x for x in tickers
                    if isinstance(x, dict)
                    and x.get("symbol")
                    and x.get("turnover") is not None
                ],
                key=lambda x: float(x.get("turnover", 0) or 0),
                reverse=True
            )

            top = ranked[:5]

            Clock.schedule_once(
                lambda dt: self.update_success(
                    len(usdt_contracts),
                    len(tickers),
                    price,
                    mark,
                    volume,
                    turnover,
                    top
                )
            )

        except Exception as e:

            error = str(e)

            Clock.schedule_once(
                lambda dt: self.update_error(error)
            )

    def update_success(
        self, contracts, ticker_count,
        price, mark, volume, turnover, top
    ):

        self.status.text = "Status: FUTURES LIVE"
        self.status.color = (0, 1, 0, 1)

        self.signal.text = (
            "LBANK USDT PERPETUAL\n\n"
            f"BTCUSDT Price: {float(price):,.4f}\n"
            f"Mark Price: {float(mark or 0):,.4f}"
        )

        self.details.text = (
            f"USDT Contracts: {contracts}\n"
            f"Live Tickers: {ticker_count}\n"
            f"BTC Volume: {volume}\n"
            f"BTC Turnover: {turnover}\n\n"
            "TOP 5 BY TURNOVER:\n" +
            "\n".join(
                f"{x['symbol']}: {float(x['turnover']):,.0f}"
                for x in top
            )
        )

        self.risk.text = "Trading signals: Not active"

        self.btn.disabled = False

    def update_error(self, error):

        self.status.text = "Status: ERROR"
        self.status.color = (1, 0, 0, 1)

        self.signal.text = "FUTURES API ERROR\n\n" + error[:250]

        self.details.text = "Waiting for next test"
        self.btn.disabled = False


class LBankScannerApp(App):

    def build(self):
        self.title = "LBank Futures Scanner"
        return ScannerUI()


if __name__ == "__main__":
    LBankScannerApp().run()
