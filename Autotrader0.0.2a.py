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
ws.send(json.dumps({'type': 'subscribe', 'product_ids': ['ETH-EUR', 'LTC-EUR', 'BTC-EUR']}))    #wysłanie subskrybcji


def KonektorWebsocket():
    
                                          #odebranie danych jako str
  #wyświetlenie danych w sposób uporządkowany

    x=0
    while x < 100:
        dane=ws.recv()
        c.execute('SELECT MAX(id) AS ilosc FROM tabelka'); 
        db_size=c.fetchone()    
        idfordb=db_size[0]+1
        c.execute("INSERT INTO tabelka(id, Dane) VALUES (?,?)", (idfordb, dane))
        dane=json.loads(dane)                               #uporządkowanie danych jako json( huj wie co to robi)
        print(json.dumps(dane, indent=4, sort_keys=True))        
        x=x+1       
    conn.commit()
while True:
    KonektorWebsocket()
    
