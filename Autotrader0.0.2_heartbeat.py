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
ws.send(json.dumps({"type": "subscribe","product_ids": ["ETH-USD", "ETH-EUR",'LTC-EUR'], "channels": ["level2", "heartbeat", {"name": "ticker", "product_ids": ["ETH-BTC", "ETH-USD",'LTC-EUR']}]}))    #wysłanie subskrybcji


def KonektorWebsocket():
    dane=ws.recv()                                      #odebranie danych jako str
    #dane=json.loads(dane)                               #uporządkowanie danych jako json( huj wie co to robi)
    #print(json.dumps(dane, indent=4, sort_keys=True))   #wyświetlenie danych w sposób uporządkowany
    c.execute('SELECT MAX(id) AS ilosc FROM tabelka'); 
    db_size=c.fetchone()    
    idfordb=db_size[0]+1
    print(idfordb)
    c.execute("INSERT INTO tabelka(id, Dane) VALUES (?,?)", (idfordb, dane))
    conn.commit()
while True:
    KonektorWebsocket()


    
