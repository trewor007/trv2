# This Python file uses the following encoding: utf-8

import platform
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

conn=sqlite3.connect('bazadanych.db')
c = conn.cursor()
q = queue.Queue()
api_key=gdax_sandbox_key
secret_key=gdax_sandbox_API_secret
passphrase=gdax_sandbox_phassphrase

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
        self.thread=Thread.Thread(target=_go, name='Websocket')
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
class CBProAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = ''.join([timestamp, request.method, request.path_url, (request.body or '')])
        request.headers.update(get_auth_headers(timestamp, message, self.api_key, self.secret_key, self.passphrase))
        return request
def get_auth_headers(timestamp, message, api_key, secret_key, passphrase):
    message = message.encode('ascii')
    hmac_key = base64.b64decode(secret_key)
    signature = hmac.new(hmac_key, message, hashlib.sha256)
    signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')
    return {'Content-Type': 'Application/JSON', 'CB-ACCESS-SIGN': signature_b64, 'CB-ACCESS-TIMESTAMP': timestamp, 'CB-ACCESS-KEY': api_key, 'CB-ACCESS-PASSPHRASE': passphrase}
class Public_Requester():
    """
    Wszystkie zapytania niewymagające logowanie przesyłane są tą klasą
    """
    def __init__(self, url='https://api.pro.coinbase.com', timeout=30, produkty='BTC-EUR', start=None, end=None, skala=None):
        self.url = url.rstrip('/')
        self.auth = None
        self.session = requests.Session()
        self.timeout = timeout
        self.produkty= produkty # uwaga! zamiennie używane z product_id. kandydat do usunięcia
        self.skala=skala        # uwaga! Używanie jedynie przy danych historycznych. kandydat do usunięcia
        self.start=start        # uwaga! Używanie jedynie przy danych historycznych. kandydat do usunięcia
        self.end=end            # uwaga! Używanie jedynie przy danych historycznych. kandydat do usunięcia

    def Produkty(self):
        """
        Lista możliwych par walutowych
        """
        return self._Request('get','/products')
    def Czas(self):
        """
        Podaje aktualny czas na serwerze    
        """
        return self._Request('get', '/time')
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
            while end < end_tmp:
                start=end
                end=start+(300*skala)
                k=(k+self.Historic_rates(start, end, skala, produkt))
                time.sleep(0.4)
            else:
                end=end_tmp
                k=(k+self.Historic_rates(start, end, skala, produkt))
                return k                
        else:   
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
class Private_Requester(Public_Requester):
    """
    Wszystkie zapytania po zalogowaniu przesyłane są tą klasą(jeżeli w nawiasie powyżej jest "Public_Pequester" to zapytania z tej klasy są obsługiwane przez _Requester z tamtej klasy
    """
    def __init__(self, api_key, secret_key, passphrase, url='https://api.pro.coinbase.com'):
        super(Private_Requester, self).__init__(url)
        self.auth=CBProAuth(api_key, secret_key, passphrase)
        self.session=requests.session()
    def get_konto(self, account_id):
        """
        Pobiera informacje na temat pojedyńczego konta

        Wejście:
                account_id (str): nazwa poszukiwanego konta
        Wyjście:
                Dane konta (dict)
        """
        return self._Request('get','/accounts/'+account_id)

    def get_konta(self):
        """
        jw tylko dla wielu
        """
        return self.get_konto('')
    def zlecenie(self, product_id, side, order_type, **kwargs):
        """
        Składanie zamówienia. główny konstruktor wszystkie rodzaje zamówień składane są tutaj po czym przechodzą do innej klasy gdzie są wysyłane

        Wejście:
                produkty (str): para produktów na której składamy zamówienie[BTC-EUR]
                side (str): 'buy'/'sell'
        DO UZUPEŁNIENIE!!!
        """
        params={'product_id':product_id, 'side':side, 'type':order_type}
        params.update(kwargs)
        return self._Request('post', '/orders', data=json.dumps(params))
    def zlecenie_limit(self, product_id, side, price, size, client_oid=None, stp=None, time_in_force=None, cancel_after=None, post_only=None, overdraft_enabled=None, funding_amount=None):
        """
        Składanie zamówienia typu limit(jedyny dopuszczalny rodzaj zamówienia dla bota)
        DO UZUPEŁNIENIE!!!
        """
        params={'product_id':product_id, 'side':side, 'order_type':'limit', 'price':price, 'size':size, 'client_oid':client_oid, 'stp':stp, 'time_in_force':time_in_force, 'cancal_after':cancel_after, 'post_only':post_only, 'overdraft_enabled':overdraft_enabled, 'funding_amount':funding_amount}
        params=dict((a, b) for a, b in params.items() if b is not None)
        return self.zlecenie(**params)
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
class Rules():
    def SMA_EMA(self, produkt_id, zakres, cena, smas_budget, smas_budget2, ema_budget, ema_budget2, smas, rsi, ema, wallet):
        smas=Si.SI_sma(cena=cena, zakres=zakres[0])             
        rsi=Si.SI_RSI(cena=cena)
        print("===========================================================")
        print("Pair: {} Rsi: {}. Cena Size: {}".format(pair, rsi, len(cena)))
        if ((cena[-1]>smas[-1]) and (cena[-1]<cena[-2]) and (smas_budget["kupiono"]==True) and (smas_budget["BuyPrice"]<cena[-1])): #sprzedawanie
            smas_budget["kupiono"]=False       
            wallet[pair[4:]]=round(wallet[pair[4:]]+(smas_budget['coin_amount']*cena[-1]),2)
            smas_budget["Sentence"]=("SMAS_SELL {} {}@ Price: {}  Buyprice: {} ".format(smas_budget["coin_amount"],pair[:3],cena[-1],smas_budget['BuyPrice']))
            smas_budget["coin_amount"]=float(0)
            smas_budget['BuyPrice']=float(0)
        elif ((cena[-1]>smas[-1]) and (cena[-1]<cena[-2]) and (rsi<30) and (smas_budget2["kupiono"]==True) and (smas_budget2["BuyPrice"]<cena[-1])): #sprzedawanie rsi
            smas_budget2["kupiono"]=False
            wallet[pair[4:]]=round(wallet[pair[4:]]+(smas_budget2['coin_amount']*cena[-1]),2)
            smas_budget2["Sentence"]=("SMAS_SELL RSI {} {}@ Price: {} Buyprice: {}".format(smas_budget2["coin_amount"],pair[:3],cena[-1],smas_budget2['BuyPrice']))
            smas_budget2["coin_amount"]=float(0)
            smas_budget2['BuyPrice']=float(0)
        elif ((cena[-1]<smas[-1]) and (cena[-1]>cena[-2]) and (smas_budget["kupiono"]==False) ): #kupowanie
            smas_budget["kupiono"]=True
            smas_budget["BuyPrice"]=cena[-1]
            smas_budget['coin_amount']=round(((0.1*wallet[pair[4:]])/cena[-1]),7)
            wallet[pair[4:]]=round(wallet[pair[4:]]-(smas_budget['coin_amount']*cena[-1]),7)
            smas_budget["Sentence"]=("SMAS_BUY  {} {}@ Price {}".format(smas_budget["coin_amount"],pair[:3],cena[-1]))
        elif ((cena[-1]<smas[-1]) and (cena[-1]>cena[-2]) and (rsi>70) and (smas_budget2["kupiono"]==False) ): #kupowanie rsi
            smas_budget2["kupiono"]=True
            smas_budget2["BuyPrice"]=cena[-1]
            smas_budget2['coin_amount']=round(((0.1*wallet[pair[4:]])/cena[-1]),7)
            wallet[pair[4:]]=round(wallet[pair[4:]]-(smas_budget2['coin_amount']*cena[-1]),7)
            smas_budget2["Sentence"]=("SMAS_BUY RSI  {} {}@ Price {}".format(smas_budget2["coin_amount"],pair[:3],cena[-1]))
        else:
            pass
        for i in zakres:
            if len(cena)>i:
                j=zakres.index(i)
                e=Si.SI_ema(cena=cena, zakres=i)
                k=e.tolist()
                ema[j].append(k[-1])
                if ((cena[-1]>ema[j][-1]) and (cena[-1]<cena[-2]) and (ema_budget[j]["kupiono"]==True) and (ema_budget[j]["BuyPrice"]<cena[-1])): #sprzedawanie
                    ema_budget[j]["kupiono"]=False
                    wallet[pair[4:]]=round(wallet[pair[4:]]+(ema_budget[j]['coin_amount']*cena[-1]),2)
                    ema_budget[j]["Sentence"]=("EMA{}_SELL {} {}@ Price: {}  Buyprice: {} ".format((j+1),ema_budget[j]["coin_amount"],pair[:3],cena[-1],ema_budget[j]['BuyPrice']))
                    ema_budget[j]["coin_amount"]=float(0)
                    ema_budget[j]['BuyPrice']=float(0)
                elif ((cena[-1]>ema[j][-1]) and (cena[-1]<cena[-2]) and (rsi<30) and (ema_budget2[j]["kupiono"]==True) and (ema_budget2[j]["BuyPrice"]<cena[-1])): #sprzedawanie rsi
                    ema_budget2[j]["kupiono"]=False
                    wallet[pair[4:]]=round(wallet[pair[4:]]+(ema_budget2[j]['coin_amount']*cena[-1]),2)
                    ema_budget2[j]["Sentence"]=("EMA{}_SELL RSI {} {}@ Price: {}  Buyprice: {} ".format((j+1),ema_budget2[j]["coin_amount"],pair[:3],cena[-1],ema_budget2[j]['BuyPrice']))
                    ema_budget2[j]["coin_amount"]=float(0)
                    ema_budget2[j]['BuyPrice']=float(0)
                elif ((cena[-1]<ema[j][-1]) and (cena[-1]>cena[-2]) and (ema_budget[j]["kupiono"]==False) ): #kupowanie
                    ema_budget[j]["kupiono"]=True
                    ema_budget[j]["BuyPrice"]=cena[-1]
                    ema_budget[j]['coin_amount']=round(((0.1*wallet[pair[4:]])/cena[-1]),7)
                    wallet[pair[4:]]=round(wallet[pair[4:]]-(ema_budget[j]['coin_amount']*cena[-1]),7)
                    ema_budget[j]["Sentence"]=("EMA{}_BUY  {} {}@ Price {}".format((j+1),ema_budget[j]["coin_amount"],pair[:3],cena[-1]))
                elif ((cena[-1]<ema[j][-1]) and (cena[-1]>cena[-2]) and (rsi>70) and (ema_budget2[j]["kupiono"]==False) ): #kupowanie rsi
                    ema_budget2[j]["kupiono"]=True
                    ema_budget2[j]["BuyPrice"]=cena[-1]
                    ema_budget2[j]['coin_amount']=round(((0.15*wallet[pair[4:]])/cena[-1]),7)
                    wallet[pair[4:]]=round(wallet[pair[4:]]-(ema_budget2[j]['coin_amount']*cena[-1]),7)
                    ema_budget2[j]["Sentence"]=("EMA{}_BUY RSI  {} {}@ Price {}".format((j+1),ema_budget2[j]["coin_amount"],pair[:3],cena[-1]))
                else:
                    pass 
        return smas_budget, smas_budget2, ema_budget, ema_budget2, smas, rsi, ema, wallet         

def Preignitor():
    end=(time.time())
    start=end-1800#86400
    for product_id in produkty:
        PR=Public_Requester()
        un_filtered=PR.Historic_rates_divider(start=start, end=end, skala=900, produkt=product_id)
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
def Plot_update(cena, czas, x):
    p[x].set_data(czas,cena)
    ax[x].relim()
    ax[x].autoscale_view()
    plt.pause(1e-3)            
def clear():
    os.system('cls')

b=False
zakres=[10, 20, 40, 80]

Si=StockIndicators()
a=int(input("[1 EUR][2 BTC]"))
if a==1:
    produkty=["BTC-EUR", "ETH-EUR", "ETC-EUR", "LTC-EUR", "BCH-EUR", "ZRX-EUR"]
elif a==2:
    produkty=["ETH-BTC", "ETC-BTC", "LTC-BTC", "BCH-BTC", "ZRX-BTC"]
wallet={'EUR':float(200),'BTC':float(0),'ETH':float(0),'ETC':float(0),'LTC':float(0),'BCH':float(0), 'ZRX':float(0)}
cena=[[] for _ in range(len(produkty))]
czas=[[] for _ in range(len(produkty))]
smas=[[] for _ in range(len(produkty))]
rsi= [[] for _ in range(len(produkty))]
ax=[[] for _ in range(len(produkty))]
p=[[] for _ in range(len(produkty))]
ema= [[] for _ in range(len(zakres))]
ema= [copy.deepcopy(ema) for _ in range(len(produkty))]
smas_budget=[{"coin_amount":int(0), "kupiono": False, "BuyPrice":0, "Sentence":None} for _ in range(len(produkty))]
smas_budget2=[{"coin_amount":int(0), "kupiono": False, "BuyPrice":0, "Sentence":None} for _ in range(len(produkty))]
ema_zakres=[{"coin_amount":int(0), "kupiono": False, "BuyPrice":0, "Sentence":None} for _ in range(len(zakres))]
ema_zakres2=[{"coin_amount":int(0), "kupiono": False, "BuyPrice":0, "Sentence":None} for _ in range(len(zakres))]
ema_budget=[copy.deepcopy(ema_zakres) for _ in range(len(produkty))]
ema_budget2=[copy.deepcopy(ema_zakres2) for _ in range(len(produkty))]
# with open("datadump.txt", "a") as myfile:
#     myfile.write("time befor preignitor {}" .format(time.time()))

Preignitor()


# with open("datadump.txt", "a") as myfile:
#     myfile.write("[{},{}]".format(czas[0], cena[0]))

if platform.system() == 'Windows':
    Preignitor_plot(produkty=produkty, cena=cena, czas=czas)
webs=MyWebsocket(produkty=produkty)
webs.start()
for x in range(len(produkty)):
    cena[x]=cena[x][::-1]
    czas[x]=czas[x][::-1]

# with open("datadump.txt", "a") as myfile:
#     myfile.write("switching to websocket")
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
        # with open("datadump.txt", "a") as myfile:
        #     myfile.write("[{},{}]".format(czas[0], cena[0]))
        if len(cena[produkt_id])>zakres[0]:
            Ru=Rules()
            Ru.SMA_EMA(produkt_id=produkt_id, zakres=zakres, cena=cena[produkt_id], smas_budget=smas_budget[produkt_id], smas_budget2=smas_budget2[produkt_id], ema_budget=ema_budget[produkt_id], ema_budget2=ema_budget2[produkt_id], smas=smas[produkt_id], rsi=rsi[produkt_id], ema=ema[produkt_id], wallet=wallet)
            for x in range(len(produkty)):
                print(smas_budget[x]["Sentence"],smas_budget2[x]["Sentence"])               
                for y in range(len(zakres)):
                    print(ema_budget[x][y]["Sentence"],ema_budget2[x][y]["Sentence"])
        else:
            pass
        if platform.system() == 'Windows':
            Plot_update(cena=cena[produkt_id], czas=czas[produkt_id], x=produkt_id)
        beta=(time.time()-alfa)
        print(beta)
        print(wallet)

