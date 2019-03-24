# This Python file uses the following encoding: utf-8
import base64
import datetime
import copy
import hmac
import h5py
import hashlib
import json
import platform
import urllib3
import urllib.request
import time
import timeit
import random
import requests
import queue
import os




import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import threading as Thread

from collections import deque
from requests.auth import AuthBase
from sklearn import preprocessing
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, Dropout, LSTM, LSTM, BatchNormalization
from tensorflow.python.keras.callbacks import TensorBoard, ModelCheckpoint
from websocket import create_connection, WebSocketConnectionClosedException




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
        runned=False
        if (int(end)-int(start)) > (300*int(skala)):
            runned=True
            end_tmp=end
            end=start+(300*skala)
            k=self.Historic_rates(start, end, skala, produkt)
            print("A Time from {} to {}".format(datetime.datetime.fromtimestamp(start).strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.fromtimestamp(end).strftime('%Y-%m-%d %H:%M:%S')))
            while end < end_tmp:
                start=end
                end=start+(300*skala)
                k=(k+self.Historic_rates(start, end, skala, produkt))
                print("B Time from {} to {}".format(datetime.datetime.fromtimestamp(start).strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.fromtimestamp(end).strftime('%Y-%m-%d %H:%M:%S')))
                time.sleep(0.4)
            else:
                end=end_tmp
                k=(k+self.Historic_rates(start, end, skala, produkt))
                print("C Time from {} to {}".format(datetime.datetime.fromtimestamp(start).strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.fromtimestamp(end).strftime('%Y-%m-%d %H:%M:%S')))
                return k                
        elif (runned==False):   
                k=self.Historic_rates(start, end, skala, produkt)
                print("D Time from {} to {}".format(datetime.datetime.fromtimestamp(start).strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.fromtimestamp(end).strftime('%Y-%m-%d %H:%M:%S')))
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
def Preignitor():
    end=(time.time())
    start=end-8640000
    for product_id in produkty:
        PR=Public_Requester()
        un_filtered=PR.Historic_rates_divider(start=start, end=end, skala=300, produkt=product_id)
        for v in range(len(un_filtered)):
            cena[produkty.index(product_id)].append(un_filtered[v])
def classify(current, future):
    if float(future)>float(current):
        return 1
    else:
        return 0
def preprocess_data_frame(data_frame):
    data_frame=data_frame.drop('future', 1)

    for col in data_frame.columns:
        print(col)
        if col !='target':
            data_frame[col]=data_frame[col].pct_change()
            data_frame.dropna(inplace=True)
            data_frame[col]=preprocessing.scale(data_frame[col].values)
    data_frame.dropna(inplace=True)
    sequential_data=[]
    prev_days=deque(maxlen=seq_len)
    for i in data_frame.values:
        prev_days.append([n for n in i[:-1]])
        if len(prev_days)==seq_len:
            sequential_data.append([np.array(prev_days), i [-1]])

    random.shuffle(sequential_data)
    buys=[]
    sells=[]
    for seq, target in sequential_data:
        if target==0:
            sells.append([seq, target])
        elif target==1:
            buys.append([seq, target])
    
    random.shuffle(buys)
    random.shuffle(sells)
    
    lower=min(len(buys), len(sells))
    buys=buys[:lower]
    sells=sells[:lower]
    sequential_data=buys+sells
    random.shuffle(sequential_data)
    
    x=[]
    y=[]
    
    for seq, target in sequential_data:
        x.append(seq)
        y.append(target)
    return np.array(x), y



produkty=['ETH-BTC']
cena=[[] for _ in range(len(produkty))]
Preignitor()
for x in range(len(produkty)):
    cena[x]=cena[x][::-1]

produkt_id=0

seq_len=60
future_period_predict=3
ratio_to_predict=produkty[0]
Epochs=10
BATCH_SIZE=64
NAME='tenserflow_model_{}'.format(time.time())

pd.set_option('display.max_rows',100)
main_frame=pd.DataFrame()
data_frame=pd.DataFrame(columns=['time', 'close_price', 'volume'])
for i in range(len(cena[produkt_id])):
     data_frame.loc[i] = [cena[produkt_id][i][0],cena[produkt_id][i][4],cena[produkt_id][i][5]]
data_frame.set_index("time", inplace=True)
data_frame['future']=data_frame['close_price'].shift(-future_period_predict)
data_frame['target']=list(map(classify, data_frame['close_price'], data_frame['future']))

times=sorted(data_frame.index.values)
last_5pct=sorted(data_frame.index.values)[-int(0.05*len(times))]
validation_data_frame=data_frame[(data_frame.index>= last_5pct)]
data_frame=data_frame[(data_frame.index< last_5pct)]

train_x, train_y = preprocess_data_frame(data_frame)
validation_x, validation_y= preprocess_data_frame(validation_data_frame)

print("train data: {} validation {}".format(len(train_x), len(validation_x)))
print("dont buy: {} Buys: {}".format(train_y.count(0), train_y.count(1)))
print("VALIDATION dont buy: {} buy {}".format(validation_y.count(0), validation_y.count(1)))

model=Sequential()
model.add(LSTM(128,input_shape=(train_x.shape[1:]), return_sequences=True))
model.add(Dropout(0.2))
model.add(BatchNormalization())

model.add(LSTM(128, return_sequences=True))
model.add(Dropout(0.1))
model.add(BatchNormalization())

model.add(LSTM(128))
model.add(Dropout(0.2))
model.add(BatchNormalization())

model.add(Dense(32, activation='relu'))
model.add(Dropout(0.2))

model.add(Dense(2,activation='softmax'))

opt=tf.keras.optimizers.Adam(lr=0.001, decay=1e-6)


#Compile Model
model.compile(
    loss='sparse_categorical_crossentropy', 
    optimizer=opt, 
    metrics=['accuracy']
)

tensorboard=TensorBoard(log_dir="logs/{}".format(NAME))

filepath="RNN_FINAL-{epoch:02d}-{val_acc:.3f}"
checkpoint=ModelCheckpoint("models/{}.model".format(filepath, monitor='val_acc', verbose=1, save_best_only=True, model='max'))

#train model
history=model.fit(
    train_x, train_y,
    batch_size=BATCH_SIZE,
    epochs=Epochs,
    validation_data=(validation_x, validation_y),
    callbacks=[tensorboard, checkpoint]
) 
 #score_model
score=model.evaluate(validation_x, validation_y, verbose=0)
print('Test loss:', score[0])
print('Test accuracy: ', score[1])

model.save("models/{}".format(NAME))












print(data_frame.head(20))




