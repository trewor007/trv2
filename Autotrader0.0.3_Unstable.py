import time
import json
import sqlite3
import urllib3
import timeit
import urllib.request
from websocket import create_connection

newdict={}

def KonektorWebsocketSubskribe():
    x=0
    while x < 1000:
        dane=json.loads(ws.recv())                                           
        b=['type', 'side', 'price', 'time', 'order_id', 'product_id', 'order_type', 'size', 'reason', 'remaining_size', 'client_oid', 'sequence']
        i=0
        while i<len(b):
           a = eval("dane.get('" + b[i] + "', None)")
           newdict[b[i]]=a
           i=i+1
        c.execute("INSERT INTO Subskribe (type, side, price, time, order_id, product_id, order_type, size, reason, remaining_size, client_oid, sequence) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (newdict["type"], newdict["side"], newdict["price"], newdict["time"],  newdict["order_id"], newdict["product_id"], newdict["order_type"], newdict["size"], newdict["reason"], newdict["remaining_size"], newdict["client_oid"], newdict["sequence"]))
        x=x+1
        print(x)

    conn.commit()
def KonektorWebsocketTicker():
    x=0
    b=['type', 'sequence', 'product_id', 'price', 'open_24h', 'volume_24h', 'low_24h', 'high_24h', 'volume_30d', 'best_bid', 'best_ask', 'side', 'time', 'trade_id', 'last_size']
    i=0
    while x<1000:
        dane=json.loads(ws.recv())
        typtranzakcji=dane.get('type',None)
        if typtranzakcji=='ticker':
            while i<len(b):
                a = eval("dane.get('" + b[i] + "', None)")

                newdict[b[i]]=a
                i=i+1
            c.execute("INSERT INTO Ticker(type, sequence, product_id, price, open_24h, volume_24h, low_24h, high_24h, volume_30d, best_bid, best_ask, side, time, trade_id, last_size) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (newdict['type'], newdict['sequence'], newdict['product_id'], newdict['price'], newdict['open_24h'], newdict['volume_24h'], newdict['low_24h'], newdict['high_24h'], newdict['volume_30d'], newdict['best_bid'], newdict['best_ask'], newdict['side'], newdict['time'], newdict['trade_id'], newdict['last_size']))
            x=x+1
            print(x)
    conn.commit()
def KonektorWebsocketLevel2():
    x=0
    while x<100:
        dane=json.loads(ws.recv())                               
        #print(json.dumps(dane, indent=4, sort_keys=True))             
        b=['type', 'product_id', 'time', 'bids', 'asks', 'changes']
        i=0
        typtranzakcji=dane.get('type',None)
        if (typtranzakcji=='snapshot' or typtranzakcji=='l2update'):        
            while i<len(b):
                print(len(b))
                a = eval("dane.get('" + b[i] + "', None)")
                newdict[b[i]]=a
                i=i+1
            c.execute("INSERT INTO l2update(type, product_id, time, bids, asks, changes) VALUES (?,?,?,?,?,?)", (newdict['type'], newdict['product_id'], newdict['time'], str(newdict['bids']), str(newdict['asks']), str(newdict['changes'])))
            x=x+1
            print(x)
    conn.commit()
def KonektorWebsocketHeartbeat():
    x=0
    while x<100:
        dane=json.loads(ws.recv())                                         
        b=["last_trade_id","product_id","sequence","time","type"]
        i=0
        while i<len(b):
            a = eval("dane.get('" + b[i] + "', None)")
            newdict[b[i]]=a
            i=i+1
        c.execute("INSERT INTO Heartbeat(type, sequence, product_id, time, last_trade_id) VALUES (?,?,?,?,?)", (newdict['type'], newdict['sequence'], newdict['product_id'], newdict['time'], newdict['last_trade_id']))
        x=x+1
        print(x)
    conn.commit()   
produkty=['ETH-EUR', 'LTC-EUR', 'BTC-EUR']
arg1 = 4
if arg1 == 0:
    kanaly =None
elif arg1 == 2:
    kanaly= "heartbeat"
elif arg1 == 3:
    kanaly=["ticker"]
elif arg1 == 4:
    kanaly="level2"
print(arg1)
conn = sqlite3.connect('bazadanych.db')     #polaczenie z baza danych
c = conn.cursor()                           # tworzy kursor o nazwie c

def tabelaKreacja():                        #tworzenie tabeli // nie używane nigdzie w programie sprawdzić funkcje CREATE TABLE IF NOT EXISTS i wstawienia bezpośrednio do programu( nie w pętli)
    c.execute("CREATE TABLE IF NOT EXISTS tabelka(ID NUMERIC, Dane TEXT,)") # nawias wywala błąd


ws=create_connection("wss://ws-feed.gdax.com")
if kanaly is None:
    ws.send(json.dumps({'type': 'subscribe', 'product_ids': produkty}))
else:
    ws.send(json.dumps({'type': 'subscribe', 'product_ids': produkty, 'channels': [{"name": kanaly, 'product_ids': produkty,}]}))    #wysłanie subskrybcji
a=time.time()
if arg1==0: 
    KonektorWebsocketSubskribe()
if arg1==2:
    KonektorWebsocketHeartbeat()
if arg1==3:
    KonektorWebsocketTicker()
if arg1==4:
    KonektorWebsocketLevel2()
b=time.time()
print(b-a)
