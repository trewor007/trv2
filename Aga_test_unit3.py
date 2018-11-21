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
import random
import copy

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import threading as Thread
from websocket import create_connection, WebSocketConnectionClosedException

conn=sqlite3.connect('bazadanych.db')
c = conn.cursor()
q = queue.Queue()
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
beta=[0]
b=False
zakres=[5, 10, 15]
czas=[]
Si=StockIndicators()
a=int(input("[1 EUR][2 BTC]"))
if a==1:
    produkty=["BTC-EUR", "ETH-EUR"]
elif a==2:
    produkty=["ETH-BTC"]
wallet={'EUR':float(200),'BTC':float(0),'ETH':float(0),'ETC':float(0),'LTC':float(0),'BCH':float(0), 'ZRX':float(0)}
cena=[[0] for _ in range(len(produkty))]
smas=[[] for _ in range(len(produkty))]
rsi= [[] for _ in range(len(produkty))]
ema= [[] for _ in range(len(zakres))]
ema= [copy.deepcopy(ema) for _ in range(len(produkty))]
smas_budget=[{"coin_amount":int(0), "kupiono": False, "BuyPrice":0, "Sentence":None} for _ in range(len(produkty))]
smas_budget2=[{"coin_amount":int(0), "kupiono": False, "BuyPrice":0, "Sentence":None} for _ in range(len(produkty))]
ema_zakres=[{"coin_amount":int(0), "kupiono": False, "BuyPrice":0, "Sentence":None} for _ in range(len(zakres))]
ema_zakres2=[{"coin_amount":int(0), "kupiono": False, "BuyPrice":0, "Sentence":None} for _ in range(len(zakres))]
ema_budget=[copy.deepcopy(ema_zakres) for _ in range(len(produkty))]
ema_budget2=[copy.deepcopy(ema_zakres2) for _ in range(len(produkty))]

#fig=plt.figure()
#ax1=fig.add_subplot(1,1,1)
#ax2=fig.add_subplot(1,1,1)
fig, ax=plt.subplots()
x=[0]
y=[0]
y1=[0]
y2=[0]
p1, =ax.plot(x,y, label='cena')
p2, =ax.plot(x,y1, label='cena2')
p3, =ax.plot(x,y2, label='czas pracy')
plt.xlabel('czas')
plt.ylabel('cena')
plt.title('wykres')
plt.legend()
plt.show(block=False)

while True:
    time.sleep(1)
    alpfa=time.time()
    #input('press enter')
    rand_produkt=random.choice(produkty) 
    rand_price=random.uniform(1.0, 5.0)
    rand_czas=time.ctime()
    alfa={'type':'ticker', 'price':rand_price, 'product_id':rand_produkt, 'time':rand_czas}
    q.put(alfa)
    if q.not_empty:            
        dane=q.get()        
        typ=dane.get('type',None)
        if typ=='ticker':
            price=dane.get('price', None)
            pair=dane.get('product_id',None)
            t=dane.get('time', None)
            b=True
    if b==True:
        b=False
        
        produkt_id=produkty.index(pair)
        cena[produkt_id].append(float(price))
        czas.append(t)

    x.append(x[-1]+.1)#nie wiem czy to potrzebne skoro dosłownie linijke wyżej robie to samo
    y.append(cena[0][-1])
    y1.append(cena[1][-1])
    y2.append(beta[-1])
    p1.set_data(x,y)
    p2.set_data(x,y1)
    p3.set_data(x,y2)
    ax.relim()
    ax.autoscale_view()
    plt.pause(1e-3)
    #plt.ion()
    #ani=animation.FuncAnimation(fig,animate,interval=10000,save_count=50)#, blit=True)repeat=True)
    #plt.show()
    #plt.pause(0.1)
    #fig.clf()
    beta.append(time.time()-alpfa)
    print(beta[-1])
