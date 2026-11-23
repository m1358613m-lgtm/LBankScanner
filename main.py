https://www.lbank.com/en-US/docs/index.html

import requests
import time

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

# ==========================================
# نسخه جایگزین با CCXT (اگر از CCXT استفاده می‌کنید، فقط این بخش را کپی کنید)
# ==========================================
# import ccxt
# def get_lbank_candles_ccxt(symbol="BTC/USDT", timeframe="15m", limit=100):
#     exchange = ccxt.lbank()
#     try:
#         return exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
#     except Exception as e:
#         print(f"خطا در CCXT: {e}")
#         return None
