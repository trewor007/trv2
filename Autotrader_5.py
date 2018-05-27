import time
import datetime
import json
import sqlite3
import urllib3
import timeit
import urllib.request
from websocket import create_connection

conn=sqlite3.connect('bazadanych.db')#polaczenie z baza danych
c = conn.cursor()                           # tworzy kursor o nazwie c

class Websocket(object):

    def __init__(self, wsurl="wss://ws-feed.gdax.com", ws=None, agi1=2, ping_start=0,produkty=['ETH-EUR', 'LTC-EUR', 'BTC-EUR'], newdict={}):
        self.wsurl = wsurl
        self.ws = None
        self.agi1=agi1
        self.ping_start=ping_start
        self.produkty=produkty
        self.newdict=newdict

    def KonektorWebsocketSubskribe(self):
        dane=json.loads(self.ws.recv())                                           
        b=['type', 'side', 'price', 'time', 'order_id', 'product_id', 'order_type', 'size', 'reason', 'remaining_size', 'client_oid', 'sequence']
        i=0
        while i<len(b):
           a = eval("dane.get('" + b[i] + "', None)")
           self.newdict[b[i]]=a
           i=i+1
        c.execute("INSERT INTO Subskribe (type, side, price, time, order_id, product_id, order_type, size, reason, remaining_size, client_oid, sequence) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (self.newdict["type"], self.newdict["side"], self.newdict["price"], self.newdict["time"],  newdict["order_id"], self.newdict["product_id"], self.newdict["order_type"], self.newdict["size"], self.newdict["reason"], self.newdict["remaining_size"], self.newdict["client_oid"], self.newdict["sequence"]))
    def KonektorWebsocketTicker(self):
        x=0
        b=['type', 'sequence', 'product_id', 'price', 'open_24h', 'volume_24h', 'low_24h', 'high_24h', 'volume_30d', 'best_bid', 'best_ask', 'side', 'time', 'trade_id', 'last_size']
        i=0
        dane=json.loads(self.ws.recv())
        typtranzakcji=dane.get('type',None)
        if typtranzakcji=='ticker':
            while i<len(b):
                a = eval("dane.get('" + b[i] + "', None)")
                self.newdict[b[i]]=a
                i=i+1
            c.execute("INSERT INTO Ticker(type, sequence, product_id, price, open_24h, volume_24h, low_24h, high_24h, volume_30d, best_bid, best_ask, side, time, trade_id, last_size) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (self.newdict['type'], self.newdict['sequence'], self.newdict['product_id'], self.newdict['price'], self.newdict['open_24h'], self.newdict['volume_24h'], self.newdict['low_24h'], self.newdict['high_24h'], self.newdict['volume_30d'], self.newdict['best_bid'], self.newdict['best_ask'], self.newdict['side'], self.newdict['time'], self.newdict['trade_id'], self.newdict['last_size']))
    def KonektorWebsocketLevel2(self):
        b=['type', 'product_id', 'time', 'bids', 'asks', 'changes']
        i=0
        typtranzakcji=dane.get('type',None)
        if (typtranzakcji=='snapshot' or typtranzakcji=='l2update'):        
            while i<len(b):
                a = eval("dane.get('" + b[i] + "', None)")
                self.newdict[b[i]]=a
                i=i+1
            c.execute("INSERT INTO l2update(type, product_id, time, bids, asks, changes) VALUES (?,?,?,?,?,?)", (self.newdict['type'], self.newdict['product_id'], self.newdict['time'], str(newdict['bids']), str(newdict['asks']), str(newdict['changes'])))
    def KonektorWebsocketHeartbeat(self):
        b=["last_trade_id","product_id","sequence","time","type"]
        i=0
        while i<len(b):
            a = eval("dane.get('" + b[i] + "', None)")
            self.newdict[b[i]]=a
            i=i+1
        c.execute("INSERT INTO Heartbeat(type, sequence, product_id, time, last_trade_id) VALUES (?,?,?,?,?)", (self.newdict['type'], self.newdict['sequence'], self.newdict['product_id'], self.newdict['time'], self.newdict['last_trade_id']))
    def tabelaKreacja():                        #tworzenie tabeli // nie używane nigdzie w programie sprawdzić funkcje CREATE TABLE IF NOT EXISTS i wstawienia bezpośrednio do programu( nie w pętli)
        c.execute("CREATE TABLE IF NOT EXISTS tabelka(ID NUMERIC, Dane TEXT,)") # nawias wywala błąd 

    def Polacz(self):
        self.ws=create_connection(self.wsurl)

        if self.agi1 == 0:
            kanaly =None
        elif self.agi1 == 1:
            kanaly= "heartbeat"
        elif self.agi1 == 2:
            kanaly=["ticker"]
        elif self.agi1 == 3:
            kanaly="level2"
        else:
            print('ERROR:WRONG ARGUMENT! (arg1)=', self.agi1)

        print(kanaly)

        if kanaly is None:
            self.ws.send(json.dumps({'type': 'subscribe', 'product_ids': self.produkty}))
        else:
            self.ws.send(json.dumps({'type': 'subscribe', 'product_ids': self.produkty, 'channels': [{"name": kanaly, 'product_ids': self.produkty,}]}))    #wysłanie subskrybcji
        while True:
            try:
                if (time.time() - self.ping_start) >= 20:
                    self.ws.ping("ping")
                    print('%s ping' % time.ctime())
                    self.ping_start = time.time()
            except ValueError as e:
                print('{} Error :{}'.format(time.ctime(), e))
            except Exception as e:
                print('{} Error :{}'.format(time.ctime(), e))
            else:
                print('%s  no ping' % time.ctime())

            dane=json.loads(self.ws.recv())

            if self.agi1==0: 
                self.KonektorWebsocketSubskribe()
            if self.agi1==1:
                self.KonektorWebsocketHeartbeat()
            if self.agi1==2:
                self.KonektorWebsocketTicker()
            if self.agi1==3:
                self.KonektorWebsocketLevel2()
            conn.commit()
            time.sleep(1)

class Autotrader():
    webs=Websocket()
    webs.Polacz()
    