import time
import datetime
import json
import sqlite3
import urllib3
import timeit
import urllib.request
import requests
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from websocket import create_connection, WebSocketConnectionClosedException, WebSocketBadStatusException, WebSocketException

conn=sqlite3.connect(":memory:")
c = conn.cursor()  
c.execute("CREATE TABLE `Ticker` (	`ID`	INTEGER PRIMARY KEY AUTOINCREMENT,	`Type`	TEXT,	`Sequence`	INTEGER,	`Product_id`	TEXT,	`Price`	INTEGER,	`Open_24h`	INTEGER,	`Volume_24h`	INTEGER,	`Low_24h`	INTEGER,	`High_24h`	INTEGER,	`Volume_30d`	INTEGER,	`Best_bid`	INTEGER,	`Best_ask`	INTEGER,	`side`	TEXT,	`time`	TEXT,	`trade_id`	INTEGER,	`last_size`	INTEGER)")

class Websocket():
    def __init__(self, wsurl="wss://ws-feed.pro.coinbase.com", n=0,dane=None, ws=None, kanaly=None, ping_start=0,produkty=['ETH-EUR', 'LTC-EUR', 'BTC-EUR'], newdict={}, bd_bot=1):
        self.wsurl = wsurl
        self.ws = None
        self.dane=dane
        self.ping_start=ping_start
        self.produkty=produkty
        self.newdict=newdict
        self.kanaly=kanaly
        self.bd_bot=bd_bot
        self.n=n
        print(self.produkty)
    def KonektorWebsocketTicker(self, dane):
        b=['type', 'sequence', 'product_id', 'price', 'open_24h', 'volume_24h', 'low_24h', 'high_24h', 'volume_30d', 'best_bid', 'best_ask', 'side', 'time', 'trade_id', 'last_size']
        i=0
        typtranzakcji=dane.get('type',None)
        if typtranzakcji=='ticker':
            while i<len(b):
                a = eval("dane.get('" + b[i] + "', None)")
                self.newdict[b[i]]=a
                i=i+1
            c.execute("INSERT INTO Ticker(type, sequence, product_id, price, open_24h, volume_24h, low_24h, high_24h, volume_30d, best_bid, best_ask, side, time, trade_id, last_size) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (self.newdict['type'], self.newdict['sequence'], self.newdict['product_id'], self.newdict['price'], self.newdict['open_24h'], self.newdict['volume_24h'], self.newdict['low_24h'], self.newdict['high_24h'], self.newdict['volume_30d'], self.newdict['best_bid'], self.newdict['best_ask'], self.newdict['side'], self.newdict['time'], self.newdict['trade_id'], self.newdict['last_size']))
  
    def _Polacz(self,n,z,x,v):
        self.ws=create_connection(self.wsurl, timeout=180)

        if self.kanaly is None:
            self.ws.send(json.dumps({'type': 'subscribe', 'product_ids': self.produkty}))
        else:
            self.ws.send(json.dumps({'type': 'subscribe', 'product_ids': self.produkty, 'channels': [{"name": self.kanaly, 'product_ids': self.produkty,}]}))    #wysłanie subskrybcji
        self._Nasluch(n,z,x,v)
    def _Nasluch(self,n,z,x,v):
        while True:
            try:
                if (time.time() - self.ping_start) >= 20:
                    self.ws.ping()
                    print('{} [   ping] {}/{}'.format(time.ctime(),z,n))
                    self.ping_start = time.time()
                    z=z+1
                    n=n+1
                else:
                    print('{} [no ping] {}/{}'.format(time.ctime(),x,n))
                    x=x+1
                    n=n+1
                dane=json.loads(self.ws.recv())
            except WebSocketConnectionClosedException as e:
                print('{} [Reconecting] {}/{}'.format(time.ctime(),v,n))
                v=v+1
                n=n+1
                self.on_error(e)
            except WebSocketBadStatusException as e:
                self.on_error(e)
            except ValueError as e:
                self.on_error(e)
            except Exception as e:
                self.on_error(e)
            self.wiadomosc(dane)
    def on_error(self, e):
        with open('error_old.txt','a') as txt_file:
            print('{} Error :{}'.format(time.ctime(), e), file=txt_file)
        time.sleep(0.4)
        self._Polacz(n,z,x,v)
    def wiadomosc(self, dane):
        if self.bd_bot==1:
           self.KonektorWebsocketTicker(dane=dane)
           conn.commit()
        elif self.bd_bot==2:
            bot=Bots()
            bot.Adria(dane=dane, smas=[])

class Autotrader():
    produkty=["ETH-BTC"]
    kanaly=["ticker"]
    bd_bot=1
    z=x=v=n=1
    webs=Websocket(produkty=produkty, kanaly=kanaly, bd_bot=bd_bot)
    webs._Polacz(n,z,x,v)
