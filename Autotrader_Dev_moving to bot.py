import time
import datetime
import json
import sqlite3
import urllib3
import timeit
import urllib.request
import requests
import numpy as np
from threading import Thread
from websocket import create_connection, WebSocketConnectionClosedException

conn=sqlite3.connect('bazadanych.db')
c = conn.cursor()


class MyWebsocket(object):

    def __init__(self, wsurl="wss://ws-feed.pro.coinbase.com", dane=None, ws=None, kanaly=None, ping_start=0,produkty=['ETH-EUR', 'LTC-EUR', 'BTC-EUR'], newdict={}, bd_bot=1):
        self.wsurl = wsurl
        self.ws = None
        self.dane=dane
        self.ping_start=ping_start
        self.produkty=produkty
        self.newdict=newdict
        self.kanaly=kanaly
        self.bd_bot=bd_bot

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
    def start(self):
        def _go():
            self._Polacz()
            self._Nasluch()
            self._Rozlacz()
        self.stop=False
        self.thread=Thread(target=_go)
        self.thread.start()

    def _Polacz(self):
        self.ws=create_connection(self.wsurl, timeout=180)

        if self.kanaly is None:
            self.ws.send(json.dumps({'type': 'subscribe', 'product_ids': self.produkty}))
        else:
            self.ws.send(json.dumps({'type': 'subscribe', 'product_ids': self.produkty, 'channels': [{"name": self.kanaly, 'product_ids': self.produkty,}]}))    #wysłanie subskrybcji
    def _Nasluch(self):
        while not self.stop:
            try:
                if (time.time() - self.ping_start) >= 20:
                    self.ws.ping()
                    self.ping_start = time.time()
                dane=json.loads(self.ws.recv())
            except ValueError as e:
                self.on_error(e)
            except Exception as e:
                self.on_error(e)
            else:
                self.on_message(dane)

    def _Rozlacz(self):
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
        pass

    def on_message(self, dane):
        print(dane)


    def on_close(self):
        if self.should_print:
            print("\n-- Socket Closed --")

    def on_error(self, e):
        with open('error.txt','a') as txt_file:
            print('{} Error :{}'.format(time.ctime(), e), file=txt_file)
        time.sleep(0.4)
        self.start()
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

class Adria(MyWebsocket):
    def __init__(self, cena=[], czas=[], smas=[], produkty="BTC-EUR"):
        self.cena=cena
        self.czas=czas
        self.produkty=produkty
    def start(produkty):
        webs=MyWebsocket(produkty=produkty, kanaly=['ticker'])
        webs.start()
        
    def on_message(self, dane):
        a=dane.get('price', None)
        t=dane.get('time', None)
        zakres=int(3)
        zakres2=int(5)
        zakres3=int(10)
        zakres4=int(20)

        if a is not None:
            self.cena.append(float(a))
            self.czas.append(t)
            if len(self.cena)>zakres:
                Si=StockIndicators()
                smas=Si.SI_sma(cena=self.cena, zakres=zakres)
                ema=Si.SI_ema(cena=self.cena, zakres=zakres)
                diff=np.subtract(smas[-1],ema[-1])

                if len(self.cena)<=zakres2:
                    print('smas: {} ema: {} '.format(round(smas[-1],6),round(ema[-1],6)))
                    print('smas/ema:{:.6f}'.format(diff))

            if len(self.cena)>zakres2:
                ema2=Si.SI_ema(cena=self.cena, zakres=zakres2)
                diff2=((ema[-1])-(ema2[-1]))
                if len(self.cena)<=zakres3:
                    print('smas: {} ema: {} ema2: {} '.format(round(smas[-1],6),round(ema[-1],6),round(ema2[-1],6)))
                    print('smas/ema:{:.6f} ema/ema2:{:.6f}'.format(diff,diff2))

            if len(self.cena)>zakres3:
                ema3=Si.SI_ema(cena=self.cena, zakres=zakres3)
                diff3=((ema2[-1])-(ema3[-1]))
                if len(self.cena)<=zakres4:
                    print('smas: {} ema: {} ema2: {} ema3:{} '.format(round(smas[-1],6),round(ema[-1],6),round(ema2[-1],6),round(ema3[-1],6)))
                    print('smas/ema:{:.6f} ema/ema2:{:.6f} ema2/ema3:{:.6f}'.format(diff,diff2,diff3))

            if len(self.cena)>zakres4:
                ema4=Si.SI_ema(cena=self.cena, zakres=zakres4)
                diff4=((ema3[-1])-(ema4[-1]))
                print('smas: {} ema: {} ema2: {} ema3:{} ema4: {}'.format(round(smas[-1],6),round(ema[-1],6),round(ema2[-1],6),round(ema3[-1],6),round(ema4[-1],6)))
                print('smas/ema:{:.6f} ema/ema2:{:.6f} ema2/ema3:{:.6f} ema3/ema4:{:.6f}'.format(diff,diff2,diff3,diff4))

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
        Adria.start(produkty=produkty)
