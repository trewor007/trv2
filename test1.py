import time
import datetime
import json
import sqlite3
import urllib3
import timeit
import urllib.request
import requests
from websocket import create_connection, WebSocketConnectionClosedException

ws=create_connection("wss://ws-feed.gdax.com")
kanaly=["ticker"]
produkty=['LTC-BTC']
ws.send(json.dumps({'type': 'subscribe', 'product_ids': produkty, 'channels': [{"name": kanaly, 'product_ids': produkty,}]}))
ping=ws.ping("pong")
print(ping)
