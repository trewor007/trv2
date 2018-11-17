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

b=False
zakres=[5, 10, 15]

Si=StockIndicators()
a=int(input("[1 EUR][2 BTC]"))
if a==1:
    produkty=["BTC-EUR", "ETH-EUR"]
elif a==2:
    produkty=["ETH-BTC"]
cena=[[] for _ in range(len(produkty))]
smas=[[] for _ in range(len(produkty))]
rsi= [[] for _ in range(len(produkty))]
ema= [[] for _ in range(len(zakres))]
ema= [copy.deepcopy(ema) for _ in range(len(produkty))]
smas_budget=[{"1coin":int(0),"2coin":int(50), "kupiono": False, "BuyPrice":0, "Sentence":None} for _ in range(len(produkty))]
smas_budget2=[{"1coin":int(0),"2coin":int(50), "kupiono": False, "BuyPrice":0, "Sentence":None} for _ in range(len(produkty))]
ema_zakres=[{"1coin":int(0),"2coin":int(50), "kupiono": False, "BuyPrice":0, "Sentence":None} for _ in range(len(zakres))]
ema_zakres2=[{"1coin":int(0),"2coin":int(50), "kupiono": False, "BuyPrice":0, "Sentence":None} for _ in range(len(zakres))]
ema_budget=[copy.deepcopy(ema_zakres) for _ in range(len(produkty))]
ema_budget2=[copy.deepcopy(ema_zakres2) for _ in range(len(produkty))]
while True:
    input('press enter')
    rand_produkt=random.choice(produkty) 
    rand_price=random.randint(1,101)
    alfa={'type':'ticker', 'price':rand_price, 'product_id':rand_produkt}
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
        alfa=time.time()
        b=False
        produkt_id=produkty.index(pair)
        cena[produkt_id].append(float(price))
        #czas.append(t)
        if len(cena[produkt_id])>zakres[0]:
            #clear()
            smas[produkt_id]=Si.SI_sma(cena=cena[produkt_id], zakres=zakres[0])                 
            rsi[produkt_id]=Si.SI_RSI(cena=cena[produkt_id])
            print("===========================================================")
            print("Pair: {} Rsi: {}. Cena Size: {}".format(pair, rsi[produkt_id], len(cena[produkt_id])))
            if ((cena[produkt_id][-1]>smas[produkt_id][-1]) and (cena[produkt_id][-1]<cena[produkt_id][-2]) and (smas_budget[produkt_id]["kupiono"]==True) and (smas_budget[produkt_id]["BuyPrice"]<cena[produkt_id][-1])): #sprzedawanie
                smas_budget[produkt_id]["kupiono"]=False       
                smas_budget[produkt_id]["2coin"]=round((smas_budget[produkt_id]["1coin"]*cena[produkt_id][-1]),2)
                smas_budget[produkt_id]["1coin"]=float(0)
                smas_budget[produkt_id]["Sentence"]=("SMAS_SELL          @ Price {}  budget  {:.7f} {} {}".format(cena[produkt_id][-1],smas_budget[produkt_id]["1coin"], pair, smas_budget[produkt_id]["2coin"]))
            elif ((cena[produkt_id][-1]>smas[produkt_id][-1]) and (cena[produkt_id][-1]<cena[produkt_id][-2]) and (rsi[produkt_id]<30) and (smas_budget2[produkt_id]["kupiono"]==True) and (smas_budget2[produkt_id]["BuyPrice"]<cena[produkt_id][-1])): #sprzedawanie rsi
                smas_budget2[produkt_id]["kupiono"]=False
                smas_budget2[produkt_id]["2coin"]=round((smas_budget2[produkt_id]["1coin"]*cena[produkt_id][-1]),2)
                smas_budget2[produkt_id]["1coin"]=float(0)
                smas_budget2[produkt_id]["Sentence"]=("SMAS_SELL RSI       @ Price {}  budget  {:.7f} {} {}".format(cena[produkt_id][-1],smas_budget2[produkt_id]["1coin"], pair, smas_budget2[produkt_id]["2coin"]))
            elif ((cena[produkt_id][-1]<smas[produkt_id][-1]) and (cena[produkt_id][-1]>cena[produkt_id][-2]) and (smas_budget[produkt_id]["kupiono"]==False) ): #kupowanie
                smas_budget[produkt_id]["kupiono"]=True
                smas_budget[produkt_id]["BuyPrice"]=cena[produkt_id][-1]
                smas_budget[produkt_id]["1coin"]=round((smas_budget[produkt_id]["2coin"]/cena[produkt_id][-1]),7)
                smas_budget[produkt_id]["2coin"]=float(0)
                smas_budget[produkt_id]["Sentence"]=("SMAS_BUY           @ Price {}  budget  {:.7f} {} {}".format(cena[produkt_id][-1],smas_budget2[produkt_id]["1coin"], pair, smas_budget2[produkt_id]["2coin"]))
            elif ((cena[produkt_id][-1]<smas[produkt_id][-1]) and (cena[produkt_id][-1]>cena[produkt_id][-2]) and (rsi[produkt_id]>70) and (smas_budget2[produkt_id]["kupiono"]==False) ): #kupowanie rsi
                smas_budget2[produkt_id]["kupiono"]=True
                smas_budget2[produkt_id]["BuyPrice"]=cena[produkt_id][-1]
                smas_budget2[produkt_id]["1coin"]=round((smas_budget2[produkt_id]["2coin"]/cena[produkt_id][-1]),7)
                smas_budget2[produkt_id]["2coin"]=float(0)
                smas_budget2[produkt_id]["Sentence"]=("SMAS_BUY     RSI   @ Price {}  budget  {:.7f} {} {}".format(cena[produkt_id][-1],smas_budget[produkt_id]["1coin"], pair, smas_budget[produkt_id]["2coin"]))
            else:
                pass
                #print("SMAS_PASS                      budget  {:.7f} 1coin.   {} 2coin".format(smas_budget[produkt_id]["1coin"],smas_budget[produkt_id]["2coin"]))
                #print("SMAS_PASS   RSI                budget  {:.7f} 1coin.   {} 2coin".format(smas_budget2[produkt_id]["1coin"],smas_budget2[produkt_id]["2coin"]))
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
                        ema_budget[produkt_id][j]["Sentence"]=("EMA{}_SELL          @ Price {}  budget  {:.7f} {} {}".format((j+1),cena[produkt_id][-1],ema_budget[produkt_id][j]["1coin"], pair, ema_budget[produkt_id][j]["2coin"]))
                    elif ((cena[produkt_id][-1]>ema[produkt_id][j][-1]) and (cena[produkt_id][-1]<cena[produkt_id][-2]) and (rsi[produkt_id]<30) and (ema_budget2[produkt_id][j]["kupiono"]==True) and (ema_budget2[produkt_id][j]["BuyPrice"]<cena[produkt_id][-1])): #sprzedawanie rsi
                        ema_budget2[produkt_id][j]["kupiono"]=False
                        ema_budget2[produkt_id][j]["2coin"]=round((ema_budget2[produkt_id][j]["1coin"]*cena[produkt_id][-1]),2)
                        ema_budget2[produkt_id][j]["1coin"]=float(0)
                        ema_budget2[produkt_id][j]["Sentence"]=("EMA{}_SELL  RSI     @ Price {}  budget  {:.7f} {} {}".format((j+1),cena[produkt_id][-1],ema_budget[produkt_id][j]["1coin"], pair, ema_budget[produkt_id][j]["2coin"]))
                    elif ((cena[produkt_id][-1]<ema[produkt_id][j][-1]) and (cena[produkt_id][-1]>cena[produkt_id][-2]) and (ema_budget[produkt_id][j]["kupiono"]==False) ): #kupowanie
                        ema_budget[produkt_id][j]["kupiono"]=True
                        ema_budget[produkt_id][j]["BuyPrice"]=cena[produkt_id][-1]
                        ema_budget[produkt_id][j]["1coin"]=round((ema_budget[produkt_id][j]["2coin"]/cena[produkt_id][-1]),7)
                        ema_budget[produkt_id][j]["2coin"]=float(0)
                        ema_budget[produkt_id][j]["Sentence"]=("EMA{}_BUY           @ Price {}  budget  {:.7f} {} {}".format((j+1),cena[produkt_id][-1],ema_budget[produkt_id][j]["1coin"], pair, ema_budget[produkt_id][j]["2coin"]))
                    elif ((cena[produkt_id][-1]<ema[produkt_id][j][-1]) and (cena[produkt_id][-1]>cena[produkt_id][-2]) and (rsi[produkt_id]>70) and (ema_budget2[produkt_id][j]["kupiono"]==False) ): #kupowanie rsi
                        ema_budget2[produkt_id][j]["kupiono"]=True
                        ema_budget2[produkt_id][j]["BuyPrice"]=cena[produkt_id][-1]
                        ema_budget2[produkt_id][j]["1coin"]=round((ema_budget2[produkt_id][j]["2coin"]/cena[produkt_id][-1]),7)
                        ema_budget2[produkt_id][j]["2coin"]=float(0)
                        ema_budget2[produkt_id][j]["Sentence"]=("EMA{}_BUY    RSI    @ Price {}  budget  {:.7f} {} {}".format((j+1),cena[produkt_id][-1],ema_budget2[produkt_id][j]["1coin"], pair, ema_budget2[produkt_id][j]["2coin"]))
                    else:
                        pass
                        #print("EMA{}_PASS                      budget  {:.7f} 1coin.   {} 2coin".format((j+1),ema_budget[produkt_id][j]["1coin"],ema_budget[produkt_id][j]["2coin"]))
                        #print("EMA{}_PASS   RSI                budget  {:.7f} 1coin.   {} 2coin".format((j+1),ema_budget2[produkt_id][j]["1coin"],ema_budget2[produkt_id][j]["2coin"]))
            for x in range(len(produkty)):
                print(smas_budget[x]["Sentence"])
                print(smas_budget2[x]["Sentence"])                
                for y in range(len(zakres)):
                    print(ema_budget[x][y]["Sentence"])        
                    print(ema_budget2[x][y]["Sentence"])     
        else:
            pass
        beta=(time.time()-alfa)
        print(beta)

