""" Pobieranie i przetwarzanie danych z ksiegi zamowien kanalu l2
    
    Wejscie:
    Wyjscie:
"""
import threading as Thread
import queue
import time
import json #wprowadzone na potrzeby testow
from websocket import create_connection, WebSocketConnectionClosedException
#import MyWebsocket

q = queue.Queue()

class MyWebsocket(object):
    """ Klasa odpowiedzialna za polaczenia z modulem Websocket 
        Wejscie:

        Wyjscie:
            
            """

    def __init__(self, wsurl="wss://ws-feed.pro.coinbase.com", dane=None, ws=None, kanaly=None, ping_start=0, produkty=['ETH-EUR', 'LTC-EUR', 'BTC-EUR'], newdict={}):
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
        self.ws.send(json.dumps({"type": "subscribe", "product_ids": self.produkty, "channels": [{ "name": self.kanaly, "product_ids": self.produkty}]}))    #wysyłanie subskrybcji DO ZMODYFIKOWANIA TAK ABY PRZYJMOWALO DOWOLNY ZESTAW KANALOW

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
            print(e)
            with open('error_MyWebsocket.txt','a') as txt_file:
                print('{} Disconnect: {}'.format(time.ctime(), e), file=txt_file)
            pass

        self.on_close()

    def close(self):
        self.stop= True
        self.thread.join()

    def on_open(self):
        print("-- Subscribed! --\n")   
    
    def on_message(self, dane):
        q.put(dane)    #KANDYDAT DO ZMIANY
    
    def on_close(self):
        print("\n-- Socket Closed --")            
    def on_error(self, e):
        print(e)
        with open('error_MyWebsocket.txt','a') as txt_file:
            print('{} Error: {}'.format(time.ctime(), e), file=txt_file)
        webs=MyWebsocket(produkty=self.produkty, kanaly=self.kanaly)
        webs.start() 

class Order_Book():
    produkty=['BCH-EUR']
    kanaly="level2"       
    webs=MyWebsocket(produkty=produkty, kanaly=kanaly)
    webs.start()
    
    while True:
        if q.not_empty:            
            dane=q.get()            
            TypTranzakcji=(dane.get('type',None))
            if TypTranzakcji=="snapshot":
                print('snapshot')
                Asks=dane.get('asks',None)                          #Baza cen za sprzedaży             Ten element ma rosnąć
                Bids=dane.get('bids', None)                         #Baza cen kupna                    Ten Element ma maleć
                for num, c in enumerate(Asks):                      #zmiana z str na float dla l2update
                    Asks[num]=list(map(float, c))
                for num, c in enumerate(Bids):                      #zmiana z str na float dla l2update
                    Bids[num]=list(map(float, c))                
            if TypTranzakcji=='l2update':
                print('l2update')
                Zmiana=(dane.get('changes'))
                Zmiana=[[Zmiana[0][0], float(Zmiana[0][1]), float(Zmiana[0][2])]]    #zmiana z str na float dla changes. dO WYWALENIA ZEWNĘTRZNE NAWIASY
                JuzJest=False
                if Zmiana[0][0]=='sell':                                           #jeżeli zmiana dotyczy sprzedaży
                    zListy=Asks
                else:        zListy=Bids
                for num, data in enumerate(zListy):                                       #przejżyj tabele 
                    if data[0]==Zmiana[0][1] and Zmiana[0][2]!=0.0:                                 #jeżeli cena z aktualizacji znajduje się już w tabeli
                        data[1]=Zmiana[0][2]                                   #zamień ilość waluty po tej cenie na tą z aktualizacji
                        JuzJest=True
                    if data[0]==Zmiana[0][1] and Zmiana[0][2]==0.0:   #jeżeli ilość waluty z aktualizacji wynosi zero
                        zListy.pop(num)                                                   #usuń daną pozycje z tabeli
                        JuzJest=True
                if JuzJest==False and Zmiana[0][0]=='sell':
                    for num, data in enumerate(zListy):
                        if Zmiana[0][1]<data[0] :     #Ask
                            zListy.insert(num, Zmiana[0][1:])
                            break
                        elif num==(len(zListy)-1):
                            zListy.append(Zmiana[0][1:])
                            break
                        else:
                            pass
                if JuzJest==False and Zmiana[0][0]=='buy':
                    for num, data in enumerate(zListy):
                        if Zmiana[0][1]>data[0] :      #Bid
                            zListy.insert(num, Zmiana[0][1:])
                            break
                        elif num==(len(zListy)-1):
                            zListy.append(Zmiana[0][1:])
                            break
                        else:
                            pass

