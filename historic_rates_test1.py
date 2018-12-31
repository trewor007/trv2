import time
import datetime
import json
import urllib3
import urllib.request
import requests
produkty=["BTC-EUR", "ETH-EUR", "ETC-EUR", "LTC-EUR", "BCH-EUR", "ZRX-EUR"]
class Requester():
    def __init__(self, url='https://api.pro.coinbase.com', timeout=30, produkty='BTC-EUR', start=None, end=None, skala=None, bd_bot=None ):
        self.url = url.rstrip('/')
        self.auth = None
        self.session = requests.Session()
        self.timeout = timeout
        self.produkty= produkty

    def _Request(self, method ,endpoint, params=None, data=None):
        """
        Wysyła zapytanie do strony. Po dojściu do tego momentu nastąpi wyjście z klasy

        Wejście:
                    method (str):   Metoda HTTP (get, post, delete)
                    endpoint (str): końcówka adresu HTTP odpowiednia do zapytania
                    params (dict):  dodatkowe parametry do zapytania HTTP (opcionalne)
                    data (str):     parametry w formacie JSON do zapytania HTTP typu POST (opcionalne)
        Wyjście:
                    odpowiedz w formacie JSON (list/dict)
        """
        url=self.url+endpoint
        r=self.session.request(method, url, params=params, data=data, auth=self.auth, timeout=30)
        return r.json()
    def Historic_rates_divider(self, start, end, skala, produkt):
        """
        Rozdziela pobieranie danych historycznych dla pojedyńczego produktu na mniejsze kawałki (max 300 świeczek) 
        po czym łączy zebrane dane i zwraca je jako pojedyńczy większy zbiór danych

        Wejście:
                start (float): początek przedziału czasowego z którego mają zostać pobrane dane w formacie epoch
                end (float): koniec przedziału czasowego z którego mają zostać pobrane dane w formacie epoch
                skala (int): rama czasowa pojedyńczej świeczki
                produkt (str): nazwa wyszukiwanego produktu (BTC-EUR)
        Wyjście:
                lista list [czas w formacie epoch, najniższa cena, najwyższa cena, cena otwarcia, cena zamknięcia, wolumen]
        """
        if (int(end)-int(start)) > (300*int(skala)):
            end_tmp=end
            end=start+(300*skala)
            k=self.Historic_rates(start, end, skala, produkt)
            while end < end_tmp:
                start=end
                end=start+(300*skala)
                k=(k+self.Historic_rates(start, end, skala, produkt))
                time.sleep(0.4)
            else:
                end=end_tmp
                k=(k+self.Historic_rates(start, end, skala, produkt))
                return k                
        else:   
                k=self.Historic_rates(start, end, skala, produkt)
                return k
    def Historic_rates(self, start, end, skala, produkt):
        """
        Pobiera dane historyczne dla pojedyńczego produktu w formie świeczek(max 300 pozycji)

        Wejście:
                start (float): początek przedziału czasowego z którego mają zostać pobrane dane w formacie epoch
                end (float): koniec przedziału czasowego z którego mają zostać pobrane dane w formacie epoch
                skala (int): rama czasowa pojedyńczej świeczki
                produkt (str): nazwa wyszukiwanego produktu (BTC-EUR)
        Wyjście:
                lista list [czas w formacie epoch, najniższa cena, najwyższa cena, cena otwarcia, cena zamknięcia, wolumen]
        """
        parametry={}
        start=datetime.datetime.fromtimestamp(start).isoformat()
        end=datetime.datetime.fromtimestamp(end).isoformat()
        print(start, end)
        if start is not None:
            parametry['start'] = start
        if end is not None:
            parametry['end'] = end
        if skala is not None:
            dozwolona_skala=[60, 300, 900, 3600, 21600, 86400]
            if skala not in dozwolona_skala:
                nowa_skala = min(dozwolona_skala, key=lambda x:abs(x-skala))
                print('{} Wartosc {} dla skali niedozwolona, uzyto wartosci {}'.format(time.ctime(), skala, nowa_skala))
                skala = nowa_skala
            parametry['granularity']= skala
        print(parametry)
        return self._Request('GET','/products/{}/candles'.format(str(produkt)), params=parametry)

#start=1542207000
#end=1542653400
Req=Requester()

cena=[[] for _ in range(len(produkty))]
def Preignitor():
    end=time.time()
    start=end-86400
    for product_id in produkty:
        un_filtered=Req.Historic_rates_divider(start, end, skala=900, produkt=product_id)
        for v in range(len(un_filtered)):
            cena[produkty.index(product_id)].append(un_filtered[v][4])
            time.sleep(1)
#print(json.dumps(z, indent=3))


