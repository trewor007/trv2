import time
import json
import sqlite3
import urllib3
import urllib.request
from websocket import create_connection


conn = sqlite3.connect('bazadanych.db')     #polaczenie z baza danych
c = conn.cursor()                           # tworzy kursor o nazwie c

def tabelaKreacja():                        #tworzenie tabeli // nie używane nigdzie w programie sprawdzić funkcje CREATE TABLE IF NOT EXISTS i wstawienia bezpośrednio do programu( nie w pętli)
    c.execute("CREATE TABLE IF NOT EXISTS tabelka(ID NUMERIC, Dane TEXT,)") # nawias wywala błąd


ws=create_connection("wss://ws-feed.gdax.com")                                                  #połączenie z podaną stroną
ws.send(json.dumps({"type": "subscribe", "channels": [{"name": "ticker", "product_ids": ['ETH-EUR', 'LTC-EUR', 'BTC-EUR'],}]}))    #wysłanie subskrybcji


def KonektorWebsocket():
    dane=ws.recv()                                      #odebranie danych jako str
    dane=json.loads(dane)                               #uporządkowanie danych jako json( huj wie co to robi)
    print(json.dumps(dane, indent=4, sort_keys=True))   #wyświetlenie danych w sposób uporządkowany
    #c.execute('SELECT MAX(id) AS ilosc FROM tabelka3'); 
    #db_size=c.fetchone()    
    #print(db_size)
    #c.execute("INSERT INTO tabelka3(Dane) VALUES (?)", (wpis,))
    #conn.commit()
while True:
    KonektorWebsocket()
    #time.sleep(0.15)

    
    #"channels": [{"name": "level2", "product_ids": ["BTC-EUR"],}]
