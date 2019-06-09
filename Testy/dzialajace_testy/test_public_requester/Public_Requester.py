import datetime
import requests
import time

class Public_Requester(object):
    """
    Wszystkie zapytania niewymagające logowanie przesyłane są tą klasą
    """
    def __init__(self, url='https://api.pro.coinbase.com', timeout=30, produkty='BTC-EUR', start=None, end=None, skala=None):
        self.url = url.rstrip('/')
        self.auth = None
        self.session = requests.Session()
        self.timeout = timeout
        self.produkty= produkty # uwaga! zamiennie używane z product_id. kandydat do usunięcia
        self.skala=skala        # uwaga! Używanie jedynie przy danych historycznych. kandydat do usunięcia
        self.start=start        # uwaga! Używanie jedynie przy danych historycznych. kandydat do usunięcia
        self.end=end            # uwaga! Używanie jedynie przy danych historycznych. kandydat do usunięcia
    def Produkty(self):
        """
        Lista możliwych par walutowych
        """
        return self._Request('get','/products')
    def Czas(self):
        """
        Podaje aktualny czas na serwerze    
        """
        return self._Request('get', '/time')
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
        runned=False
        if (int(end)-int(start)) > (200*int(skala)):
            runned=True
            true_end=end
            end=start+(200*skala)
            if produkt[3]!='-':                              #Uodparnia program na błąd niepoprawnego znaku pomiędzy parami liczbowymi
                produkt=produkt[0:3]+'-'+produkt[4:]
            else:
                pass
            k=self.Historic_rates(start, end, skala, produkt)
            k=k[::-1]
            print("A Time from {} to {}".format(datetime.datetime.fromtimestamp(start).strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.fromtimestamp(end).strftime('%Y-%m-%d %H:%M:%S')))
            while end+(200*skala) < true_end:
                start=end
                end=start+(200*skala)
                L=self.Historic_rates(start, end, skala, produkt)
                L=L[::-1]
                k=k+L
                print("B Time from {} to {}".format(datetime.datetime.fromtimestamp(start).strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.fromtimestamp(end).strftime('%Y-%m-%d %H:%M:%S')))
                time.sleep(0.4)
            else:
                start=end
                end=true_end
                L=self.Historic_rates(start, end, skala, produkt)
                L=L[::-1]
                k=k+L
                print("C Time from {} to {}".format(datetime.datetime.fromtimestamp(start).strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.fromtimestamp(end).strftime('%Y-%m-%d %H:%M:%S')))
                return k                
        elif (runned==False):   
                k=self.Historic_rates(start, end, skala, produkt)
                k=k[::-1]
                print("D Time from {} to {}".format(datetime.datetime.fromtimestamp(start).strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.fromtimestamp(end).strftime('%Y-%m-%d %H:%M:%S')))
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
        return self._Request('GET','/products/{}/candles'.format(str(produkt)), params=parametry)
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
        #print(r.text)
        return r.json()
