import time
import json
import sqlite3
import urllib3
import urllib.request
from websocket import create_connection

conn = sqlite3.connect('bazadanych.db')     #polaczenie z baza danych
c = conn.cursor()                           # tworzy kursor o nazwie c


ws=create_connection("wss://ws-feed.gdax.com")                                                  #połączenie z podaną stroną
ws.send(json.dumps({'type': 'subscribe', 'product_ids': ['ETH-EUR', 'LTC-EUR', 'BTC-EUR']}))    #wysłanie subskrybcji


def KonektorWebsocket():
    dane=ws.recv()                                      #odebranie danych jako str
    dane=json.loads(dane)                               #uporządkowanie danych jako json( huj wie co to robi)
    print(json.dumps(dane, indent=4, sort_keys=True))   #wyświetlenie danych w sposób uporządkowany

 
while True:
    KonektorWebsocket()
    
