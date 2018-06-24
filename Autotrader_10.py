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

conn=sqlite3.connect('bazadanych.db')
c = conn.cursor()


class Websocket():

    def __init__(self, wsurl="wss://ws-feed.gdax.com", dane=None, ws=None, kanaly=None, ping_start=0,produkty=['ETH-EUR', 'LTC-EUR', 'BTC-EUR'], newdict={}, bd_bot=1):
        self.wsurl = wsurl
        self.ws = None
        self.dane=dane
        self.ping_start=ping_start
        self.produkty=produkty
        self.newdict=newdict
        self.kanaly=kanaly
        self.bd_bot=bd_bot
        print(self.produkty)
    def KonektorWebsocketSubskribe(self, dane):
        b=['type', 'side', 'price', 'time', 'order_id', 'product_id', 'order_type', 'size', 'reason', 'remaining_size', 'client_oid', 'sequence']
        i=0
        while i<len(b):
           a = eval("dane.get('" + b[i] + "', None)")
           self.newdict[b[i]]=a
           i=i+1
        c.execute("INSERT INTO Subskribe (type, side, price, time, order_id, product_id, order_type, size, reason, remaining_size, client_oid, sequence) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (self.newdict["type"], self.newdict["side"], self.newdict["price"], self.newdict["time"],  self.newdict["order_id"], self.newdict["product_id"], self.newdict["order_type"], self.newdict["size"], self.newdict["reason"], self.newdict["remaining_size"], self.newdict["client_oid"], self.newdict["sequence"]))
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
    def KonektorWebsocketLevel2(self, dane):
        b=['type', 'product_id', 'time', 'bids', 'asks', 'changes']
        i=0
        typtranzakcji=dane.get('type',None)
        if (typtranzakcji=='snapshot' or typtranzakcji=='l2update'):
            while i<len(b):
                a = eval("dane.get('" + b[i] + "', None)")
                self.newdict[b[i]]=a
                i=i+1
            c.execute("INSERT INTO l2update(type, product_id, time, bids, asks, changes) VALUES (?,?,?,?,?,?)", (self.newdict['type'], self.newdict['product_id'], self.newdict['time'], str(self.newdict['bids']), str(self.newdict['asks']), str(self.newdict['changes'])))
    def KonektorWebsocketHeartbeat(self, dane):
        b=["last_trade_id","product_id","sequence","time","type"]
        i=0
        while i<len(b):
            a = eval("dane.get('" + b[i] + "', None)")
            self.newdict[b[i]]=a
            i=i+1
        c.execute("INSERT INTO Heartbeat(type, sequence, product_id, time, last_trade_id) VALUES (?,?,?,?,?)", (self.newdict['type'], self.newdict['sequence'], self.newdict['product_id'], self.newdict['time'], self.newdict['last_trade_id']))
    def tabelaKreacja():                        #tworzenie tabeli // nie używane nigdzie w programie sprawdzić funkcje CREATE TABLE IF NOT EXISTS i wstawienia bezpośrednio do programu( nie w pętli)
        c.execute("CREATE TABLE IF NOT EXISTS tabelka(ID NUMERIC, Dane TEXT,)") # nawias wywala błąd
        pass
    def _Polacz(self):
        self.ws=create_connection(self.wsurl, timeout=180)

        if self.kanaly is None:
            self.ws.send(json.dumps({'type': 'subscribe', 'product_ids': self.produkty}))
        else:
            self.ws.send(json.dumps({'type': 'subscribe', 'product_ids': self.produkty, 'channels': [{"name": self.kanaly, 'product_ids': self.produkty,}]}))    #wysłanie subskrybcji
        self.Nasluch()
    def Nasluch(self):
        while True:
            try:
                if (time.time() - self.ping_start) >= 20:
                    self.ws.ping()
                    self.ping_start = time.time()
                dane=json.loads(self.ws.recv())
            except WebSocketConnectionClosedException as e:
                self.on_error(e)
            except WebSocketBadStatusException as e:
                self.on_error(e)
            except ValueError as e:
                self.on_error(e)
            except Exception as e:
                self.on_error(e)
            self.wiadomosc(dane)
    def on_error(self, e):
        with open('error.txt','a') as txt_file:
            print('{} Error :{}'.format(time.ctime(), e), file=txt_file)
        time.sleep(0.4)
        self._Polacz()
    def wiadomosc(self, dane):
        if self.bd_bot==1:
           if self.kanaly==None:
                self.KonektorWebsocketSubskribe(dane=dane)
           elif self.kanaly=="heartbeat":
                self.KonektorWebsocketHeartbeat(dane=dane)
           elif self.kanaly==["ticker"]:
                self.KonektorWebsocketTicker(dane=dane)
           elif self.kanaly=="level2":
                self.KonektorWebsocketLevel2(dane=dane)
           conn.commit()
        elif self.bd_bot==2:
            bot=Bots()
            bot.Adria(dane=dane)
class Requester():
    def __init__(self, url='https://api.gdax.com', timeout=30, produkty='BTC-EUR', start=None, end=None, skala=None, bd_bot=None ):
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
class Bots():
    def __init__(self, cena=[], czas=[]):
        self.cena=cena
        self.czas=czas
    def Adria(self, dane):
        a=dane.get('price', None)
        t=dane.get('time', None)
        zakres=int(20)
        zakres2=int(40)
        zakres3=int(60)
        zakres4=int(120)
        if a is not None:
            self.cena.append(float(a))
            self.czas.append(t)
            if len(self.cena)>zakres:
                weights=np.ones((zakres,))/zakres
                smas=np.convolve(self.cena, weights, 'valid')

                weights_ema = np.exp(np.linspace(-1.,0.,zakres))
                weights_ema /= weights_ema.sum()
                ema=np.convolve(self.cena,weights_ema)[:len(self.cena)]
                ema[:zakres]=ema[zakres]

                if len(self.cena)<zakres2:
                    print('smas: {} ema: {} '.format(smas[-1],ema[-1]))

            if len(self.cena)>zakres2:

                weights_ema2 = np.exp(np.linspace(-1.,0.,zakres2))
                weights_ema2 /= weights_ema2.sum()
                ema2=np.convolve(self.cena,weights_ema2)[:len(self.cena)]
                ema2[:zakres2]=ema[zakres2]

                if len(self.cena)<zakres3:
                    print('smas: {} ema: {} ema2: {} '.format(smas[-1],ema[-1],ema2[-1]))

            if len(self.cena)>zakres3:

                weights_ema3 = np.exp(np.linspace(-1.,0.,zakres3))
                weights_ema3 /= weights_ema3.sum()
                ema3=np.convolve(self.cena,weights_ema3)[:len(self.cena)]
                ema3[:zakres3]=ema[zakres3]
                if len(self.cena)<zakres4:
                    print('smas: {} ema: {} ema2: {} ema3:{} '.format(smas[-1],ema[-1],ema2[-1],ema3[-1]))

            if len(self.cena)>zakres4:

                weights_ema4 = np.exp(np.linspace(-1.,0.,zakres4))
                weights_ema4 /= weights_ema4.sum()
                ema4=np.convolve(self.cena,weights_ema4)[:len(self.cena)]
                ema4[:zakres4]=ema[zakres4]

                print('smas: {} ema: {} ema2: {} ema3:{} ema4: {}'.format(smas[-1],ema[-1],ema2[-1],ema3[-1],ema4[-1]))
            #
            #    if self.cena[-1]>smas[-1]:
            #        print("sprzedaje")
            #    if self.cena[-1]<smas[-1]:
            #        print('kupuje')
            #    else:
            #        print('wait')
        else:
            pass


class Autotrader():
    print("zapisywanie do bazy danych czy uzyte przez bota? ")
    bd_bot=int(input("[1 Baza danych] [2 Adria]"))
    print("Podaj pare walut ktore chcesz wykorzystac")
    a=int(input("[1 BTC-EUR] [2 LTC-EUR] [3 LTC-BTC] [4 ETH-EUR] [5 ETH-BTC] [6 BCH-BTC] [7 BCH-EUR]"))
    if a==1:
        produkty=["BTC-EUR"]
    elif a==2:
        produkty=["LTC-EUR"]
    elif a==3:
        produkty=["LTC-BTC"]
    elif a==4:
        produkty=["ETH-EUR"]
    elif a==5:
        produkty=["ETH-BTC"]
    elif a==6:
        produkty=["BCH-BTC"]
    elif a==7:
        produkty=["BCH-EUR"]
    if bd_bot==1:
        b=input("[1 Websocket] [2 Historic rates] ")
        if b=='1':
            d=int(input("[1 subskribe] [2 heartbit] [3 ticker] [4 Level2] "))

            if d == 1:
                kanaly =None
            elif d == 2:
                kanaly= "heartbeat"
            elif d == 3:
                kanaly=["ticker"]
            elif d == 4:
                kanaly="level2"
            else:
                print('ERROR:WRONG ARGUMENT! (c)=', c)
            webs=Websocket(produkty=produkty, kanaly=kanaly, bd_bot=bd_bot)
            webs._Polacz()
        elif b=='2':
            start=time.mktime(time.strptime(input("podaj Poczatek   [dd-mm-rrrr hh:mm] "), '%d-%m-%Y %H:%M'))
            end=time.mktime(time.strptime(input("podaj Koniec   [dd-mm-rrrr hh:mm] "), '%d-%m-%Y %H:%M'))
            skala=int(input("podaj rozdzielczosc [60, 300, 900, 3600, 21600, 86400]"))
            webr=Requester(produkty=produkty, start=start, end=end, skala=skala, bd_bot=bd_bot)
            webr.Historic_rates_divider()
    elif bd_bot==2:
        webs=Websocket(produkty=produkty, kanaly=['ticker'], bd_bot=bd_bot)
        webs._Polacz()
