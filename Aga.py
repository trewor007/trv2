import time
import datetime
import json
import sqlite3
import urllib3
import timeit
import urllib.request
import requests
import queue
import os

import numpy as np
import threading as Thread
from websocket import create_connection, WebSocketConnectionClosedException

conn=sqlite3.connect('bazadanych.db')
c = conn.cursor()
q = queue.Queue()

class MyWebsocket(object):

    def __init__(self, wsurl="wss://ws-feed.pro.coinbase.com", dane=None, ws=None, kanaly=None, ping_start=0,produkty=['ETH-EUR', 'LTC-EUR', 'BTC-EUR'], newdict={}, bd_bot=1):
        self.wsurl = wsurl
        self.ws = None
        self.dane=dane
        self.ping_start=ping_start
        self.produkty=produkty
        self.newdict=newdict
        self.kanaly=kanaly
    
    def start(self):
        def _go():
            self._connect()
            self._listen()
            self._disconnect()

        self.stop=False
        self.on_open()
        self.thread=Thread.Thread(target=_go)
        self.thread.start()

    def _connect(self):
        self.ws=create_connection(self.wsurl)
        self.ws.send(json.dumps({"type": "subscribe", "product_ids": self.produkty, "channels": ["heartbeat", { "name": "ticker", "product_ids": self.produkty}]}))    #wysyłanie subskrybcji

    def _listen(self):
        while not self.stop:
            try:
                data = self.ws.recv()
                dane = json.loads(data)
            except ValueError as e:
                self.on_error(e)
            except Exception as e:
                self.on_error(e)
            else:
                self.on_message(dane)
    def _disconnect(self):
        try:
            if self.ws:
                self.ws.close()
        except WebSocketConnectionClosedException as e:
            pass

        self.on_close()

    def close(self):
        self.stop= True
        self.thread.join()

    def on_open(self):
        print("-- Subscribed! --\n")   
    
    def on_message(self, dane):
        q.put(dane)
    
    def on_close(self):
        if self.should_print:
            print("\n-- Socket Closed --")            
    def on_error(self, e):
        with open('error.txt','a') as txt_file:
            print('{} Error :{}'.format(time.ctime(), e), file=txt_file)

class Requester():
    def __init__(self, url='https://api.pro.coinbase.com', timeout=30, produkty='BTC-EUR', start=None, end=None, skala=None, bd_bot=None ):
        self.url = url.rstrip('/')
        self.timeout = timeout
        self.produkty= produkty
        self.skala=skala
        self.start=start
        self.end=end
    def _get(self, path, params= None, ):
        r= requests.get(self.url + path, params=params, timeout=self.timeout).json()
        self.Printer(r)
    def Historic_rates_divider(self, x=300):
        if self.end-self.start > x*self.skala:
            self.end_tmp=self.end
            self.end=self.start+(x*self.skala)
            self.Historic_rates()
            while self.end < self.end_tmp:
                self.start=self.end
                self.end=self.start+(x*self.skala)
                self.Historic_rates()
            else:
                self.end=self.end_tmp
                self.Historic_rates()
        else:
                self.Historic_rates()
    def Historic_rates(self):
        parametry={}
        start=datetime.datetime.fromtimestamp(self.start)
        print(start)
        end=datetime.datetime.fromtimestamp(self.end)
        print(end)
        if start is not None:
            parametry['start'] = start
        if end is not None:
            parametry['end'] = end
        if self.skala is not None:
            dozwolona_skala=[60, 300, 900, 3600, 21600, 86400]
            if self.skala not in dozwolona_skala:
                nowa_skala = min(dozwolona_skala, key=lambda x:abs(x-self.skala))
                print('{} Wartosc {} dla skali niedozwolona, uzyto wartosci {}'.format(time.ctime(), skala, nowa_skala))
                self.skala = nowa_skala
            parametry['granularity']= self.skala
        self._get('/products/{}/candles'.format(str(self.produkty[0])), params=parametry)
    def Printer(self, r=None):
        i=0
        while i < len(r):
            c.execute("INSERT INTO Candles(product_id, time, low, high, open, close, volume) VALUES(?,?,?,?,?,?,?)", (self.produkty[0], r[i][0], r[i][1], r[i][2], r[i][3], r[i][4], r[i][5]))
            i=i+1
        conn.commit()
class StockIndicators():
    def SI_sma(self, cena, zakres):
        self.cena=cena
        weights=np.ones((zakres,))/zakres
        smas=np.convolve(self.cena, weights, 'valid')
        return smas
        
    def SI_ema(self, cena, zakres):
        self.cena=cena
        weights_ema = np.exp(np.linspace(-1.,0.,zakres))
        weights_ema /= weights_ema.sum()
        ema=np.convolve(self.cena,weights_ema)[:len(self.cena)]
        ema[:zakres]=ema[zakres]
        return ema

    def SI_RSI (self, cena, zakres=14):
        deltas = np.diff(cena)
        seed = deltas[:zakres+1]
        up = seed[seed >= 0].sum()/zakres
        down = -seed[seed < 0].sum()/zakres
        rs = up/down
        rsi = np.zeros_like(cena)
        rsi[:zakres] = 100. - 100./(1. + rs)

        for i in range(zakres, len(cena)):
            delta = deltas[i - 1]  # cause the diff is 1 shorter
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta
 
            up = (up*(zakres - 1) + upval)/zakres
            down = (down*(zakres - 1) + downval)/zakres
            rs = up/down
            rsi[i] = 100. - 100./(1. + rs)
        if len(cena) > zakres:
            return rsi[-1]
        else:
            return 50 
def clear():
    os.system('cls')
smas_budget=    {"1coin":int(0),"2coin":int(50), "kupiono": False, "BuyPrice":0}
ema_budget=     [{"1coin":int(0),"2coin":int(50), "kupiono": False, "BuyPrice":0},{"1coin":int(0),"2coin":int(50), "kupiono": False, "BuyPrice":0},{"1coin":int(0),"2coin":int(50), "kupiono": False, "BuyPrice":0},{"1coin":int(0),"2coin":int(50), "kupiono": False, "BuyPrice":0}]
smas_budget2=    {"1coin":int(0),"2coin":int(50), "kupiono": False, "BuyPrice":0}
ema_budget2=     [{"1coin":int(0),"2coin":int(50), "kupiono": False, "BuyPrice":0},{"1coin":int(0),"2coin":int(50), "kupiono": False, "BuyPrice":0},{"1coin":int(0),"2coin":int(50), "kupiono": False, "BuyPrice":0},{"1coin":int(0),"2coin":int(50), "kupiono": False, "BuyPrice":0}]
ema=[[],[],[],[]]
b=False
cena=[]
czas=[]
smas=[]
zakres=[10, 20, 40, 80]

Si=StockIndicators()
print("Podaj pare walut ktore chcesz wykorzystac")
a=int(input("[1 BTC-EUR] [2 LTC-EUR] [3 LTC-BTC] [4 ETH-EUR] [5 ETH-BTC] [6 BCH-BTC] [7 BCH-EUR]"))
if a==1:
    produkty=["BTC-EUR", "ETH-EUR", "ETC-EUR", "LTC-EUR", "BCH-EUR", "ZRX-EUR"]
elif a==2:
    produkty=["ETH-BTC", "ETC-BTC", "LTC-BTC", "BCH-BTC", "ZRX-BTC"]

webs=MyWebsocket(produkty=produkty)
webs.start()  
while True:
    if q.not_empty:            
        dane=q.get()        
        typ=dane.get('type',None)
        if typ=='ticker':
            price=dane.get('price', None)
            t=dane.get('time', None)
            b=True
    if b==True:
        alfa=time.time()
        b=False
        cena.append(float(price))
        #czas.append(t)
        if len(cena)>zakres[0]:
            clear()
            smas=Si.SI_sma(cena=cena, zakres=zakres[0])                 
            rsi=Si.SI_RSI(cena=cena)
            print("===========================================================")
            print("Rsi: {}. Cena Size: {}".format(rsi, len(cena)))
            if ((cena[-1]>smas[-1]) and (cena[-1]<cena[-2]) and (smas_budget["kupiono"]==True) and (smas_budget["BuyPrice"]<cena[-1])): #sprzedawanie
                smas_budget["kupiono"]=False       
                smas_budget["2coin"]=round((smas_budget["1coin"]*cena[-1]),2)
                smas_budget["1coin"]=float(0)
                print("SMAS_SELL          @ Price {}  budget  {:.7f} 1coin.   {} 2coin".format(cena[-1],smas_budget["1coin"],smas_budget["2coin"]))
            elif ((cena[-1]>smas[-1]) and (cena[-1]<cena[-2]) and (rsi<30) and (smas_budget2["kupiono"]==True) and (smas_budget2["BuyPrice"]<cena[-1])): #sprzedawanie rsi
                smas_budget2["kupiono"]=False
                smas_budget2["2coin"]=round((smas_budget2["1coin"]*cena[-1]),2)
                smas_budget2["1coin"]=float(0)
                print("SMAS_SELL RSI       @ Price {}  budget  {:.7f} 1coin.   {} 2coin".format(cena[-1],smas_budget2["1coin"],smas_budget2["2coin"]))
            elif ((cena[-1]<smas[-1]) and (cena[-1]>cena[-2]) and (smas_budget["kupiono"]==False) ): #kupowanie
                smas_budget["kupiono"]=True
                smas_budget["BuyPrice"]=cena[-1]
                smas_budget["1coin"]=round((smas_budget["2coin"]/cena[-1]),7)
                smas_budget["2coin"]=float(0)
                print("SMAS_BUY           @ Price {}  budget  {:.7f} 1coin.   {} 2coin".format(cena[-1],smas_budget2["1coin"],smas_budget2["2coin"]))
            elif ((cena[-1]<smas[-1]) and (cena[-1]>cena[-2]) and (rsi>70) and (smas_budget2["kupiono"]==False) ): #kupowanie rsi
                smas_budget2["kupiono"]=True
                smas_budget2["BuyPrice"]=cena[-1]
                smas_budget2["1coin"]=round((smas_budget2["2coin"]/cena[-1]),7)
                smas_budget2["2coin"]=float(0)
                print("SMAS_BUY     RSI   @ Price {}  budget  {:.7f} 1coin.   {} 2coin".format(cena[-1],smas_budget["1coin"],smas_budget["2coin"]))
            else:
                print("SMAS_PASS                      budget  {:.7f} 1coin.   {} 2coin".format(smas_budget["1coin"],smas_budget["2coin"]))
                print("SMAS_PASS    RSI               budget  {:.7f} 1coin.   {} 2coin".format(smas_budget2["1coin"],smas_budget2["2coin"]))
            for i in zakres:                
                if len(cena)>i:
                    j=zakres.index(i)
                    e=Si.SI_ema(cena=cena, zakres=i)
                    k=e.tolist()
                    ema[j].append(k[-1])
                    if ((cena[-1]>ema[j][-1]) and (cena[-1]<cena[-2]) and (ema_budget[j]["kupiono"]==True) and (ema_budget[j]["BuyPrice"]<cena[-1])): #sprzedawanie
                        ema_budget[j]["kupiono"]=False
                        ema_budget[j]["2coin"]=round((ema_budget[j]["1coin"]*cena[-1]),2)
                        ema_budget[j]["1coin"]=float(0)
                        print("EMA{}_SELL          @ Price {}  budget  {:.7f} 1coin.   {} 2coin".format((j+1),cena[-1],ema_budget[j]["1coin"],ema_budget[j]["2coin"]))
                    elif ((cena[-1]>ema[j][-1]) and (cena[-1]<cena[-2]) and (rsi<30) and (ema_budget2[j]["kupiono"]==True) and (ema_budget2[j]["BuyPrice"]<cena[-1])): #sprzedawanie rsi
                        ema_budget2[j]["kupiono"]=False
                        ema_budget2[j]["2coin"]=round((ema_budget2[j]["1coin"]*cena[-1]),2)
                        ema_budget2[j]["1coin"]=float(0)
                        print("EMA{}_SELL  RSI     @ Price {}  budget  {:.7f} 1coin.   {} 2coin".format((j+1),cena[-1],ema_budget[j]["1coin"],ema_budget[j]["2coin"]))
                    elif ((cena[-1]<ema[j][-1]) and (cena[-1]>cena[-2]) and (ema_budget[j]["kupiono"]==False) ): #kupowanie
                        ema_budget[j]["kupiono"]=True
                        ema_budget[j]["BuyPrice"]=cena[-1]
                        ema_budget[j]["1coin"]=round((ema_budget[j]["2coin"]/cena[-1]),7)
                        ema_budget[j]["2coin"]=float(0)
                        print("EMA{}_BUY           @ Price {}  budget  {:.7f} 1coin.   {} 2coin".format((j+1),cena[-1],ema_budget[j]["1coin"],ema_budget[j]["2coin"]))
                    elif ((cena[-1]<ema[j][-1]) and (cena[-1]>cena[-2]) and (rsi>70) and (ema_budget2[j]["kupiono"]==False) ): #kupowanie rsi
                        ema_budget2[j]["kupiono"]=True
                        ema_budget2[j]["BuyPrice"]=cena[-1]
                        ema_budget2[j]["1coin"]=round((ema_budget2[j]["2coin"]/cena[-1]),7)
                        ema_budget2[j]["2coin"]=float(0)
                        print("EMA{}_BUY    RSI    @ Price {}  budget  {:.7f} 1coin.   {} 2coin".format((j+1),cena[-1],ema_budget2[j]["1coin"],ema_budget2[j]["2coin"]))
                    else:
                        print("EMA{}_PASS                      budget  {:.7f} 1coin.   {} 2coin".format((j+1),ema_budget[j]["1coin"],ema_budget[j]["2coin"]))
                        print("EMA{}_PASS   RSI                budget  {:.7f} 1coin.   {} 2coin".format((j+1),ema_budget2[j]["1coin"],ema_budget2[j]["2coin"]))
        else:
            pass
        beta=(time.time()-alfa)
        print(beta)

