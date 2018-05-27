import time
import json
import sqlite3
import urllib3
import timeit
import urllib.request
from websocket import create_connection

def KonektorWebsocketSubskribe():
    x=0
    while x < 1000:
        dane=json.loads(ws.recv()) #pobieranie danych 
        typtranzakcji=dane.get('type',None)
        kupsprzedaj=dane.get('side',None)
        orderid=dane.get('order_id',None)
        cena=dane.get('price',None)
        czas=dane.get('time',None)
        parawalut=dane.get('product_id',None)
        typzamowienia=dane.get('order_type',None)
        rozmiar=dane.get('size',None)
        powod=dane.get('reason',None)
        rozmiar2=dane.get('remaining_size',None)
        klientoid=dane.get('client_oid',None)
        sekwencja=dane.get('sequence',None)
        c.execute("INSERT INTO Subskribe(type, side, price, time, order_id, product_id, order_type, size, reason, remaining_size, client_oid, sequence) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (typtranzakcji, kupsprzedaj, cena, czas, orderid, parawalut, typzamowienia, rozmiar, powod, rozmiar2, klientoid, sekwencja))
        x=x+1
        print(x)
    conn.commit()
def KonektorWebsocketTicker():
    x=0
    while x<10:
        dane=json.loads(ws.recv())
        typtranzakcji=dane.get('type',None)
        if typtranzakcji=='ticker':
            typtranzakcji=dane.get('type',None)
            sekwencja=dane.get('sequence',None)
            parawalut=dane.get('product_id',None)
            cena=dane.get('price',None)
            otwarcie_24h=dane.get('open_24h',None)
            rozmiar_24h=dane.get('volume_24h',None)
            nisko_24h=dane.get('low_24h',None)
            wysoko_24h=dane.get('high_24h',None)
            rozmiar_30d=dane.get('volume_30d',None)
            naj_sprzedarz=dane.get('best_bid',None)
            naj_zapytanie=dane.get('best_ask',None)
            kupsprzedaj=dane.get('side',None)
            czas=dane.get('time',None)
            id_tranzakcji=dane.get('trade_id',None)
            ost_rozmiar=dane.get('last_size',None)      
            c.execute("INSERT INTO Ticker(type, sequence, product_id, price, open_24h, volume_24h, low_24h, high_24h, volume_30d, best_bid, best_ask, side, time, trade_id, last_size) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (typtranzakcji, sekwencja, parawalut, cena, otwarcie_24h, rozmiar_30d, nisko_24h, wysoko_24h, rozmiar_30d, naj_sprzedarz, naj_zapytanie, kupsprzedaj, czas, id_tranzakcji, ost_rozmiar))
            x=x+1
            print(x)
    conn.commit()
def KonektorWebsocketlevel2():
    x=0
    while x<100:
        wpis=ws.recv()                                      #odebranie danych jako str
        #dane=json.loads(dane)                               #uporządkowanie danych jako json( huj wie co to robi)
        #print(json.dumps(dane, indent=4, sort_keys=True))   #wyświetlenie danych w sposób uporządkowany
        c.execute("INSERT INTO l2update(Dane) VALUES (?)", (wpis,))
        x=x+1
        print(x)
    conn.commit()
def KonektorWebsocketHeartbeat():
    x=0
    while x<100:
        wpis=ws.recv()                                      #odebranie danych jako str
        #dane=json.loads(dane)                               #uporządkowanie danych jako json( huj wie co to robi)
        #print(json.dumps(dane, indent=4, sort_keys=True))   #wyświetlenie danych w sposób uporządkowany
        c.execute("INSERT INTO heartbeat(Dane) VALUES (?)", (wpis,))
        x=x+1
        print(x)
    conn.commit()   
produkty=['ETH-EUR', 'LTC-EUR', 'BTC-EUR']
arg1 = 3
if arg1 == 0:
    kanaly =None
elif arg1 == 2:
    kanaly= "heartbeat"
elif arg1 == 3:
    kanaly=["ticker"]
elif arg1 == 4:
    kanaly="level2"
print(arg1)
conn = sqlite3.connect('bazadanych.db')     #polaczenie z baza danych
c = conn.cursor()                           # tworzy kursor o nazwie c

def tabelaKreacja():                        #tworzenie tabeli // nie używane nigdzie w programie sprawdzić funkcje CREATE TABLE IF NOT EXISTS i wstawienia bezpośrednio do programu( nie w pętli)
    c.execute("CREATE TABLE IF NOT EXISTS tabelka(ID NUMERIC, Dane TEXT,)") # nawias wywala błąd


ws=create_connection("wss://ws-feed.gdax.com")
if kanaly is None:
    ws.send(json.dumps({'type': 'subscribe', 'product_ids': produkty}))
else:
    ws.send(json.dumps({'type': 'subscribe', 'product_ids': produkty, 'channels': [{"name": kanaly, 'product_ids': produkty,}]}))    #wysłanie subskrybcji
a=time.time()
if arg1==0: 
    KonektorWebsocketSubskribe()
if arg1==2:
    KonektorWebsocketHeartbeat()
if arg1==3:
    KonektorWebsocketTicker()
if arg1==4:
    KonektorWebsocketL2update()
b=time.time()
print(b-a)
