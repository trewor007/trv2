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
import copy
import hmac
import hashlib
import base64
import matplotlib.pyplot as plt
import numpy as np
import threading as Thread
from requests.auth import AuthBase
from hashtag_generator import gdax_sandbox_key, gdax_sandbox_API_secret, gdax_sandbox_phassphrase
from websocket import create_connection, WebSocketConnectionClosedException

q = queue.Queue()

b=False

produkty=["BTC-EUR", "ETH-EUR", "ETC-EUR"]
ax=[[] for _ in range(len(produkty))]
p=[[] for _ in range(len(produkty))]
cena=[[] for _ in range(len(produkty))]
czas=[[] for _ in range(len(produkty))]

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
        print(e)
        with open('error_run_forever.txt','a') as txt_file:
            print('{} Error :{}'.format(time.ctime(), e), file=txt_file)
        
        webs=MyWebsocket(produkty=produkty)
        webs.start() 
class Public_Requester():
    """
    Wszystkie zapytania niewymagające logowanie przesyłane są tą klasą
    """
    def __init__(self, url='https://api.pro.coinbase.com', timeout=30, produkty='BTC-EUR', start=None, end=None, skala=None):
        self.url = url.rstrip('/')
        self.auth = None
        self.session = requests.Session()
        self.timeout = timeout

    def Historic_rates_divider(self, start, end, skala, produkt):
        """
        Rozdziela pobieranie danych historycznych dla pojedyńczego produktu na mniejsze kawałki (max 300 świeczek) 
        po czym łączy zebrane dane i zwraca je jako pojedyńczy większy zbiór danych

        Wejście:
                start (float): początek przedziału czasowego z którego mają zostać pobrane dane w formacie epoch
                end (float): koniec przedziału czasowego z którego mają zostać pobrane dane w formacie epoch
                skala (int): rama czasowa pojedyńczej świeczki
                produkt (str): nazwa wyszukiwanego produktu (BTC-EUR)
        Wyjście:
                lista list [czas w formacie epoch, najniższa cena, najwyższa cena, cena otwarcia, cena zamknięcia, wolumen]
        """
        if (int(end)-int(start)) > (300*int(skala)):
            end_tmp=end
            end=start+(300*skala)
            k=self.Historic_rates(start, end, skala, produkt)
            print('A start:{}'.format(datetime.datetime.fromtimestamp(start).isoformat()))
            print('A end:{}'.format(datetime.datetime.fromtimestamp(end).isoformat()))
            while end < end_tmp:
                start=end
                end=start+(300*skala)
                k=(k+self.Historic_rates(start, end, skala, produkt))
                print('B start:{}'.format(datetime.datetime.fromtimestamp(start).isoformat()))
                print('B end:{}'.format(datetime.datetime.fromtimestamp(end).isoformat()))
                time.sleep(0.4)
            else:
                end=end_tmp
                print('C start:{}'.format(datetime.datetime.fromtimestamp(start).isoformat()))
                print('C end:{}'.format(datetime.datetime.fromtimestamp(end).isoformat()))
                k=(k+self.Historic_rates(start, end, skala, produkt))
                return k                
        else:
                print('D start:{}'.format(datetime.datetime.fromtimestamp(start).isoformat()))
                print('D end:{}'.format(datetime.datetime.fromtimestamp(end).isoformat()))
                k=self.Historic_rates(start, end, skala, produkt)
                return k
    def Historic_rates(self, start, end, skala, produkt):
        """
        Pobiera dane historyczne dla pojedyńczego produktu w formie świeczek(max 300 pozycji)

        Wejście:
                start (float): początek przedziału czasowego z którego mają zostać pobrane dane w formacie epoch
                end (float): koniec przedziału czasowego z którego mają zostać pobrane dane w formacie epoch
                skala (int): rama czasowa pojedyńczej świeczki
                produkt (str): nazwa wyszukiwanego produktu (BTC-EUR)
        Wyjście:
                lista list [czas w formacie epoch, najniższa cena, najwyższa cena, cena otwarcia, cena zamknięcia, wolumen]
        """
        parametry={}
        start=datetime.datetime.fromtimestamp(start).isoformat()
        end=datetime.datetime.fromtimestamp(end).isoformat()
        if start is not None:
            parametry['start'] = start
        if end is not None:
            parametry['end'] = end
        if skala is not None:
            dozwolona_skala=[60, 300, 900, 3600, 21600, 86400]
            if skala not in dozwolona_skala:
                nowa_skala = min(dozwolona_skala, key=lambda x:abs(x-skala))
                print('{} Wartosc {} dla skali niedozwolona, uzyto wartosci {}'.format(time.ctime(), skala, nowa_skala))
                skala = nowa_skala
            parametry['granularity']= skala
        return self._Request('GET','/products/{}/candles'.format(str(produkt)), params=parametry)
    def _Request(self, method ,endpoint, params=None, data=None):
        """
        Wysyła zapytanie do strony. Po dojściu do tego momentu nastąpi wyjście z klasy

            Wejście:
                    method (str):   Metoda HTTP (get, post, delete)
                    endpoint (str): końcówka adresu HTTP odpowiednia do zapytania
                    params (dict):  dodatkowe parametry do zapytania HTTP (opcionalne)
                    data (str):     parametry w formacie JSON do zapytania HTTP typu POST (opcionalne)
            Wyjście:
                    odpowiedz w formacie JSON (list/dict)
        """
        url=self.url+endpoint
        r=self.session.request(method, url, params=params, data=data, auth=self.auth, timeout=30)
        #print(r.text)
        return r.json()
def Preignitor():
    end=(time.time()-3600) #-3600 because there is a 1h gap between me an the serwer
    start=end-86400
    for product_id in produkty:
        PR=Public_Requester()
        un_filtered=PR.Historic_rates_divider(start=start, end=end, skala=3600, produkt=product_id)
        time.sleep(1)
        for v in range(len(un_filtered)):
            cena[produkty.index(product_id)].append(un_filtered[v][4])
            czas[produkty.index(product_id)].append(un_filtered[v][0])
def Preignitor_plot(produkty, cena, czas):
    fig=plt.figure()
    for x in range(len(produkty)):
        ax[x]=fig.add_subplot(len(produkty), 1 , 1+x)
        
        p[x], =ax[x].plot(czas[x], cena[x])
    plt.show(block=False)
def Plot_update(produkty, cena, czas):
    for x in range(len(produkty)):
        p[x].set_data(czas[x],cena[x])
        ax[x].relim()
        ax[x].autoscale_view()
    plt.pause(1e-3)

Preignitor()
Preignitor_plot(produkty=produkty, cena=cena, czas=czas)
webs=MyWebsocket(produkty=produkty)
webs.start() 
while True:
    if q.not_empty:            
        dane=q.get()        
        typ=dane.get('type',None)
        if typ=='ticker':
            price=dane.get('price', None)
            pair=dane.get('product_id',None)
            t=dane.get('time', None)            
            if t is not None:
                t=time.mktime(time.strptime(t, '%Y-%m-%dT%H:%M:%S.%fZ'))
                b=True
    if b==True:
        alfa=time.time()
        b=False
        produkt_id=produkty.index(pair)
        cena[produkt_id].append(float(price))
        czas[produkt_id].append(t)
        Plot_update(produkty=produkty, cena=cena, czas=czas)
