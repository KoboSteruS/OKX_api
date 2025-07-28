import requests
import hmac
import base64
from datetime import datetime, timezone
import json

# Твои ключи
api_key = 'a018bfb8-1997-45db-af2e-6299bff03309'
secret_key = 'F04F7FE72491CB39E1DB88F352B82332'
passphrase = '62015326495Fred@'

# === timestamp с миллисекундами ===
timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

# Метод, путь и тело запроса
method = 'POST'
request_path = '/api/v5/trade/order'
body = {
    "instId": "BTC-USDT",
    "tdMode": "cash",
    "side": "buy",
    "ordType": "market",
    "sz": "500"
}

# === Тело в строку без пробелов ===
body_str = json.dumps(body, separators=(",", ":"))

# === Формирование подписи ===
message = f'{timestamp}{method}{request_path}{body_str}'
signature = base64.b64encode(
    hmac.new(secret_key.encode(), message.encode(), digestmod='sha256').digest()
).decode()

# === Заголовки ===
headers = {
    'OK-ACCESS-KEY': api_key,
    'OK-ACCESS-SIGN': signature,
    'OK-ACCESS-TIMESTAMP': timestamp,
    'OK-ACCESS-PASSPHRASE': passphrase,
    'Content-Type': 'application/json',
    'x-simulated-trading': '1'  # Это ВАЖНО для демо
}

# === URL для демо-режима ===
url = 'https://www.okx.com/api/v5/trade/order'

# === Отправка ===
response = requests.post(url, headers=headers, data=body_str)



print("Timestamp:", timestamp)
print("Body str:", body_str)
print("Message to sign:", message)
print("Signature:", signature)



# === Ответ ===
print("Status:", response.status_code)
print("Body:", response.text)
