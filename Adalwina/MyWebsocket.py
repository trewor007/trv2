import queue
import time
import json
import threading as Thread
from websocket import create_connection, WebSocketConnectionClosedException
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
if __name__ == "__main__":
    def on_message(self, dane):
        print(json.dumps(dane, sort_keys=True))
    pass