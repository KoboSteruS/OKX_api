import requests
import hmac
import base64
import json
import time
from datetime import datetime, timezone

# === Конфигурация ===
api_key = 'a018bfb8-1997-45db-af2e-6299bff03309'
secret_key = 'F04F7FE72491CB39E1DB88F352B82332'
passphrase = '62015326495Fred@'

BASE_URL = 'https://www.okx.com'

def get_timestamp():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

def sign(message, secret_key):
    return base64.b64encode(
        hmac.new(secret_key.encode(), message.encode(), digestmod='sha256').digest()
    ).decode()

def get_headers(method, path, body=""):
    timestamp = get_timestamp()
    message = f'{timestamp}{method}{path}{body}'
    signature = sign(message, secret_key)
    return {
        'OK-ACCESS-KEY': api_key,
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': passphrase,
        'Content-Type': 'application/json',
        'x-simulated-trading': '1'  # Удали если работаешь в боевом режиме
    }

def place_market_order(side, notional):
    path = '/api/v5/trade/order'
    url = BASE_URL + path
    body = {
        "instId": "BTC-USDT",
        "tdMode": "cash",
        "side": side,
        "ordType": "market",
        "ccy": "USDT" if side == "buy" else "BTC",
        "sz": str(notional)
    }
    body_str = json.dumps(body, separators=(",", ":"))
    print(f"{side.upper()} BODY: {body_str}")  # 👈 debug print
    headers = get_headers("POST", path, body_str)
    r = requests.post(url, headers=headers, data=body_str)
    print(f"{side.upper()} ORDER RESULT:", r.text)
    return r.json()


def get_balance(ccy):
    path = f'/api/v5/account/balance?ccy={ccy}'
    url = BASE_URL + path
    headers = get_headers("GET", path)
    r = requests.get(url, headers=headers)
    data = r.json()
    return float(data['data'][0]['details'][0]['availBal'])

# === Шаг 1: Купить на 100 USDT ===
place_market_order("buy", notional=100)

# === Шаг 2: Ждать 5 минут ===
print("Ждём 5 минут...")
time.sleep(300)

# === Шаг 3: Продать весь BTC ===
btc_balance = get_balance("BTC")
place_market_order("sell", notional=0.0009)
  # заменим notional на sz
