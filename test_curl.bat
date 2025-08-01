@echo off
curl -X POST "http://localhost:8000/api/v1/buy" -H "Content-Type: application/json" -d "{\"buy_amount\": 100, \"inst_id\": \"BTC-USDT\", \"take_profit_percent\": 5.0, \"stop_loss_percent\": 2.0}"
pause 