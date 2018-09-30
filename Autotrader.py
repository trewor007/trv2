import time
import json
import urllib3
import urllib.request
from websocket import create_connection

ws=create_connection("wss://ws-feed.gdax.com")
ws.send(json.dumps({'type': 'subscribe', 'product_ids': ['ETH-EUR', 'LTC-EUR', 'BTC-EUR']}))


def Pobieranie_danych():
    dane=ws.recv()
    dane=json.loads(dane)
    print(json.dumps(dane, indent=4, sort_keys=True))

 
while True:
    Pobieranie_danych()
{"type": "subscribe", "product_ids": [self.produkty], "channels": ["heartbeat", { "name": "ticker", "product_ids": [self.produkty]}]}

