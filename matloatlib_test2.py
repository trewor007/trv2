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
elif a==3:
    produkty=["BTC-EUR", "ETH-EUR", "ETC-EUR", "LTC-EUR", "BCH-EUR", "ZRX-EUR"]
pt=time.time()
wallet={'EUR':float(200),'BTC':float(0),'ETH':float(0),'ETC':float(0),'LTC':float(0),'BCH':float(0), 'ZRX':float(0)}
cena=[[0] for _ in range(len(produkty))]
czas=[[pt] for _ in range(len(produkty))]
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
beta=[0]
x=[0]
ax=[[] for _ in range(len(produkty))]
p=[[] for _ in range(len(produkty))]


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
"""
fig=plt.figure()
ax1=fig.add_subplot(3,1,1)
ax2=fig.add_subplot(3,1,2)
ax3=fig.add_subplot(3,1,3)
#fig, ax=plt.subplots()

p1, =ax1.plot(czas[0],cena[0], label='cena')
p2, =ax2.plot(czas[1],cena[1], label='cena2')
p3, =ax3.plot(x, beta, label='czas pracy')
#plt.xlabel('czas')
#plt.ylabel('cena')
#plt.title('wykres')
#plt.legend()
plt.show(block=False)
"""
Preignitor_plot(produkty=produkty, cena=cena, czas=czas)
while True:
    time.sleep(1)
    alpfa=time.time()
    #input('press enter')
    rand_produkt=random.choice(produkty) 
    rand_price=random.uniform(1.0, 5.0)
    rand_czas=time.time()
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
        czas[produkt_id].append(t) #zmiana
    Plot_update(produkty=produkty, cena=cena, czas=czas)
    x.append(x[-1]+.1)#nie wiem czy to potrzebne skoro dosłownie linijke wyżej robie to samo
    beta.append(time.time()-alpfa)
    print(beta[-1])
