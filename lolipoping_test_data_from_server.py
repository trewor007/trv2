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


conn=sqlite3.connect('bazadanych.db')
c = conn.cursor()
q = queue.Queue()
api_key=gdax_sandbox_key
secret_key=gdax_sandbox_API_secret
passphrase=gdax_sandbox_phassphrase

produkty=['ETH-BTC']
#Wallets()
b=False
zakres=[10, 20, 40, 80]
skala=120

wallet={'EUR':float(200),'BTC':float(0.01),'ETH':float(0),'ETC':float(0),'LTC':float(0),'BCH':float(0), 'ZRX':float(0), 'USDC':float(0)}
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
        #cena[produkt_id].append(float(price))
        if len(cena[produkt_id])==0:
            cena[produkt_id].append([0,0,0,0,0])
            cena[produkt_id][0][0]=time.time()  #Open Time
            cena[produkt_id][0][1]=price        #Open Price
            cena[produkt_id][0][2]=price        #High Price
            cena[produkt_id][0][3]=price        #Low Price
            cena[produkt_id][0][4]=price        #Close Price
        elif len(cena[produkt_id])>0:
            if price>cena[produkt_id][-1][2]:
                cena[produkt_id][-1][2]=price
                cena[produkt_id][-1][4]=price
            elif price<cena[produkt_id][-1][3]:
                cena[produkt_id][-1][3]=price
                cena[produkt_id][-1][4]=price
            elif (time.time()-cena[produkt_id][-1][0])>skala:
                cena[produkt_id].append([0,0,0,0,0])
                cena[produkt_id][-1][0]=time.time()  #Open Time
                cena[produkt_id][-1][1]=price        #Open Price
                cena[produkt_id][-1][2]=price        #High Price
                cena[produkt_id][-1][3]=price        #Low Price
                cena[produkt_id][-1][4]=price        #Close Price
            else:
                cena[produkt_id][-1][4]=price
            print(cena[produkt_id])