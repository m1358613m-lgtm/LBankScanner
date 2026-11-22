
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class ScannerUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 30
        self.spacing = 20

        self.status = Label(text="Status: Connected", color=(0, 1, 0, 1))
        self.signal = Label(text="Waiting for LBank Signal...", font_size='22sp')
        self.risk = Label(text="Risk: --%")
        
        self.btn = Button(text="Check Market", size_hint_y=None, height=100)
        self.btn.bind(on_press=self.refresh)

        self.add_widget(self.status)
        self.add_widget(self.signal)
        self.add_widget(self.risk)
        self.add_widget(self.btn)

    def refresh(self, instance):
        self.signal.text = "Scanning LBank Futures..."
        self.risk.text = "Risk: 1.5%"

class LBankScannerApp(App):
    def build(self):
        self.title = 'LBank Scanner'
        return ScannerUI()

if __name__ == '__main__':
    LBankScannerApp().run()
