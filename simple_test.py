import requests
import json

url = "http://localhost:8000/api/v1/buy"
headers = {"Content-Type": "application/json"}
data = {
    "buy_amount": 100,
    "inst_id": "BTC-USDT", 
    "take_profit_percent": 5.0,
    "stop_loss_percent": 2.0
}

try:
    response = requests.post(url, headers=headers, json=data, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}") 