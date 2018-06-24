import time
import datetime
import json
import sqlite3
import urllib3
import timeit
import urllib.request
import requests
from websocket import create_connection, WebSocketConnectionClosedException

conn=sqlite3.connect(":memory:")
c = conn.cursor()  
c.execute("CREATE TABLE `Ticker` (	`ID`	INTEGER PRIMARY KEY AUTOINCREMENT,	`Type`	TEXT,	`Sequence`	INTEGER,	`Product_id`	TEXT,	`Price`	INTEGER,	`Open_24h`	INTEGER,	`Volume_24h`	INTEGER,	`Low_24h`	INTEGER,	`High_24h`	INTEGER,	`Volume_30d`	INTEGER,	`Best_bid`	INTEGER,	`Best_ask`	INTEGER,	`side`	TEXT,	`time`	TEXT,	`trade_id`	INTEGER,	`last_size`	INTEGER)")
class Websocket():

    def __init__(self, wsurl="wss://ws-feed.gdax.com", dane= None, ws=None, agi1=2, ping_start=0,produkty=['LTC-BTC'], newdict={},n=0):
        self.wsurl = wsurl
        self.dane=dane
        self.ws = None
        self.agi1=agi1
        self.ping_start=ping_start
        self.produkty=produkty
        self.newdict=newdict
        self.n=n

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

    def Polacz(self,n,z,x,v):
        self.ws=create_connection(self.wsurl)

        if self.agi1 == 2:
            kanaly=["ticker"]

        else:
            print('ERROR:WRONG ARGUMENT! (arg1)=', self.agi1)

        

        if kanaly is None:
            self.ws.send(json.dumps({'type': 'subscribe', 'product_ids': self.produkty}))
        else:
            self.ws.send(json.dumps({'type': 'subscribe', 'product_ids': self.produkty, 'channels': [{"name": kanaly, 'product_ids': self.produkty,}]}))    #wys�anie subskrybcji
        self.Nasluch(n,z,x,v)
    def Nasluch(self, n,z,x,v):
        
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
                self.Polacz(n,z,x,v)
            except ValueError as e:
                print('{} Error: {}'.format(time.ctime(), e))
                self.Polacz(n,z,x,v)
            except Exception as e:
                print('{} Error: {}'.format(time.ctime(), e))
                self.Polacz(n,z,x,v)
          
            if self.agi1==2:
                self.KonektorWebsocketTicker(dane=dane)

            conn.commit()
            time.sleep(1)
            
        return(n,z,x,v)
class Autotrader():
    z=x=v=n=1
    produkty=["LTC-BTC"]
    webs=Websocket(produkty=produkty)
    webs.Polacz(n,z,x,v)        
