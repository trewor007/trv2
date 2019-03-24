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

Si=StockIndicators()
print("Podaj pare walut ktore chcesz wykorzystac")
a=int(input("[1 BTC-EUR] [2 LTC-EUR] [3 LTC-BTC] [4 ETH-EUR] [5 ETH-BTC] [6 BCH-BTC] [7 BCH-EUR]"))
if a==1:
    produkty=["BTC-EUR", "ETH-EUR", "ETC-EUR", "LTC-EUR", "BCH-EUR", "ZRX-EUR"]
elif a==2:
    produkty=["ETH-BTC", "ETC-BTC", "LTC-BTC", "BCH-BTC", "ZRX-BTC"]
zakres=[10, 20, 40, 80] 
cena=[[] for _ in range(len(produkty))]
smas=[[] for _ in range(len(produkty))]
rsi= [[] for _ in range(len(produkty))]
smas_budget=[{"1coin":int(0),"2coin":int(50), "kupiono": False, "BuyPrice":0} for _ in range(len(produkty))]
smas_budget2=[{"1coin":int(0),"2coin":int(50), "kupiono": False, "BuyPrice":0} for _ in range(len(produkty))]
ema_budget=[[smas_budget] for _ in range(len(zakres))]
ema_budget2=[[smas_budget] for _ in range(len(zakres))]
#ema=[[],[],[],[]]
b=False

while True:

    price=random.uniform(0,100)
    pair=random.choice(produkty)
    input("press enter")
    b=True
    if b==True:
        alfa=time.time()
        b=False
        produkt_id=produkty.index(pair)
        cena[produkt_id].append(float(price))
        #czas.append(t)
        if len(cena[produkt_id])>zakres[0]:
            clear()
            smas[produkt_id]=Si.SI_sma(cena=cena[produkt_id], zakres=zakres[0])                 
            rsi[produkt_id]=Si.SI_RSI(cena=cena[produkt_id])
            print("===========================================================")
            print("Rsi: {}. Cena Size: {}".format(rsi[produkt_id], len(cena[produkt_id])))
            if ((cena[produkt_id][-1]>smas[produkt_id][-1]) and (cena[produkt_id][-1]<cena[produkt_id][-2]) and (smas_budget[produkt_id]["kupiono"]==True) and (smas_budget[produkt_id]["BuyPrice"]<cena[produkt_id][-1])): #sprzedawanie
                smas_budget[produkt_id]["kupiono"]=False       
                smas_budget[produkt_id]["2coin"]=round((smas_budget[produkt_id]["1coin"]*cena[produkt_id][-1]),2)
                smas_budget[produkt_id]["1coin"]=float(0)
                print("SMAS_SELL          @ Price {}  budget  {:.7f} 1coin.   {} 2coin".format(cena[produkt_id][-1],smas_budget[produkt_id]["1coin"],smas_budget[produkt_id]["2coin"]))
            elif ((cena[produkt_id][-1]>smas[produkt_id][-1]) and (cena[produkt_id][-1]<cena[produkt_id][-2]) and (rsi[produkt_id]<30) and (smas_budget2[produkt_id]["kupiono"]==True) and (smas_budget2[produkt_id]["BuyPrice"]<cena[produkt_id][-1])): #sprzedawanie rsi
                smas_budget2[produkt_id]["kupiono"]=False
                smas_budget2[produkt_id]["2coin"]=round((smas_budget2[produkt_id]["1coin"]*cena[produkt_id][-1]),2)
                smas_budget2[produkt_id]["1coin"]=float(0)
                print("SMAS_SELL RSI       @ Price {}  budget  {:.7f} 1coin.   {} 2coin".format(cena[produkt_id][-1],smas_budget2[produkt_id]["1coin"],smas_budget2[produkt_id]["2coin"]))
            elif ((cena[produkt_id][-1]<smas[produkt_id][-1]) and (cena[produkt_id][-1]>cena[produkt_id][-2]) and (smas_budget[produkt_id]["kupiono"]==False) ): #kupowanie
                smas_budget[produkt_id]["kupiono"]=True
                smas_budget[produkt_id]["BuyPrice"]=cena[produkt_id][-1]
                smas_budget[produkt_id]["1coin"]=round((smas_budget[produkt_id]["2coin"]/cena[produkt_id][-1]),7)
                smas_budget[produkt_id]["2coin"]=float(0)
                print("SMAS_BUY           @ Price {}  budget  {:.7f} 1coin.   {} 2coin".format(cena[produkt_id][-1],smas_budget2[produkt_id]["1coin"],smas_budget2[produkt_id]["2coin"]))
            elif ((cena[produkt_id][-1]<smas[produkt_id][-1]) and (cena[produkt_id][-1]>cena[produkt_id][-2]) and (rsi[produkt_id]>70) and (smas_budget2[produkt_id]["kupiono"]==False) ): #kupowanie rsi
                smas_budget2[produkt_id]["kupiono"]=True
                smas_budget2[produkt_id]["BuyPrice"]=cena[produkt_id][-1]
                smas_budget2[produkt_id]["1coin"]=round((smas_budget2[produkt_id]["2coin"]/cena[produkt_id][-1]),7)
                smas_budget2[produkt_id]["2coin"]=float(0)
                print("SMAS_BUY     RSI   @ Price {}  budget  {:.7f} 1coin.   {} 2coin".format(cena[produkt_id][-1],smas_budget[produkt_id]["1coin"],smas_budget[produkt_id]["2coin"]))
            else:
                print("SMAS_PASS                      budget  {:.7f} 1coin.   {} 2coin".format(smas_budget[produkt_id]["1coin"],smas_budget[produkt_id]["2coin"]))
                print("SMAS_PASS    RSI               budget  {:.7f} 1coin.   {} 2coin".format(smas_budget2[produkt_id]["1coin"],smas_budget2[produkt_id]["2coin"]))
            for i in zakres:                
                if len(cena[produkt_id])>i:
                    j=zakres.index(i)
                    e=Si.SI_ema(cena=cena[produkt_id], zakres=i)
                    k=e.tolist()
                    ema[produkt_id][j].append(k[-1])
                    if ((cena[produkt_id][-1]>ema[produkt_id][j][-1]) and (cena[produkt_id][-1]<cena[produkt_id][-2]) and (ema_budget[produkt_id][j]["kupiono"]==True) and (ema_budget[produkt_id][j]["BuyPrice"]<cena[produkt_id][-1])): #sprzedawanie
                        ema_budget[produkt_id][j]["kupiono"]=False
                        ema_budget[produkt_id][j]["2coin"]=round((ema_budget[produkt_id][j]["1coin"]*cena[produkt_id][-1]),2)
                        ema_budget[produkt_id][j]["1coin"]=float(0)
                        print("EMA{}_SELL          @ Price {}  budget  {:.7f} 1coin.   {} 2coin".format((j+1),cena[produkt_id][-1],ema_budget[produkt_id][j]["1coin"],ema_budget[produkt_id][j]["2coin"]))
                    elif ((cena[produkt_id][-1]>ema[produkt_id][j][-1]) and (cena[produkt_id][-1]<cena[produkt_id][-2]) and (rsi[produkt_id]<30) and (ema_budget2[produkt_id][j]["kupiono"]==True) and (ema_budget2[produkt_id][j]["BuyPrice"]<cena[produkt_id][-1])): #sprzedawanie rsi
                        ema_budget2[produkt_id][j]["kupiono"]=False
                        ema_budget2[produkt_id][j]["2coin"]=round((ema_budget2[produkt_id][j]["1coin"]*cena[produkt_id][-1]),2)
                        ema_budget2[produkt_id][j]["1coin"]=float(0)
                        print("EMA{}_SELL  RSI     @ Price {}  budget  {:.7f} 1coin.   {} 2coin".format((j+1),cena[produkt_id][-1],ema_budget[produkt_id][j]["1coin"],ema_budget[produkt_id][j]["2coin"]))
                    elif ((cena[produkt_id][-1]<ema[produkt_id][j][-1]) and (cena[produkt_id][-1]>cena[produkt_id][-2]) and (ema_budget[produkt_id][j]["kupiono"]==False) ): #kupowanie
                        ema_budget[produkt_id][j]["kupiono"]=True
                        ema_budget[produkt_id][j]["BuyPrice"]=cena[produkt_id][-1]
                        ema_budget[produkt_id][j]["1coin"]=round((ema_budget[produkt_id][j]["2coin"]/cena[produkt_id][-1]),7)
                        ema_budget[produkt_id][j]["2coin"]=float(0)
                        print("EMA{}_BUY           @ Price {}  budget  {:.7f} 1coin.   {} 2coin".format((j+1),cena[produkt_id][-1],ema_budget[produkt_id][j]["1coin"],ema_budget[produkt_id][j]["2coin"]))
                    elif ((cena[produkt_id][-1]<ema[produkt_id][j][-1]) and (cena[produkt_id][-1]>cena[produkt_id][-2]) and (rsi[produkt_id]>70) and (ema_budget2[produkt_id][j]["kupiono"]==False) ): #kupowanie rsi
                        ema_budget2[produkt_id][j]["kupiono"]=True
                        ema_budget2[produkt_id][j]["BuyPrice"]=cena[produkt_id][-1]
                        ema_budget2[produkt_id][j]["1coin"]=round((ema_budget2[produkt_id][j]["2coin"]/cena[produkt_id][-1]),7)
                        ema_budget2[produkt_id][j]["2coin"]=float(0)
                        print("EMA{}_BUY    RSI    @ Price {}  budget  {:.7f} 1coin.   {} 2coin".format((j+1),cena[produkt_id][-1],ema_budget2[produkt_id][j]["1coin"],ema_budget2[produkt_id][j]["2coin"]))
                    else:
                        print("EMA{}_PASS                      budget  {:.7f} 1coin.   {} 2coin".format((j+1),ema_budget[produkt_id][j]["1coin"],ema_budget[produkt_id][j]["2coin"]))
                        print("EMA{}_PASS   RSI                budget  {:.7f} 1coin.   {} 2coin".format((j+1),ema_budget2[produkt_id][j]["1coin"],ema_budget2[produkt_id][j]["2coin"]))
        else:
            pass
        beta=(time.time()-alfa)
        print(beta)

