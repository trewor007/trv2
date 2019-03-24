import requests
import json

class Public_Requester():
    #"""
    #Wszystkie zapytania niewymagaj�ce logowanie przesy�ane s� t� klas�
    #"""
    def __init__(self, url='https://api-public.sandbox.pro.coinbase.com', timeout=30, produkty='BTC-EUR', start=None, end=None, skala=None):
        self.url = url.rstrip('/')
        self.auth = None
        self.session = requests.Session()
        self.timeout = timeout


    def Produkty(self):
        #"""
        #Lista mo�liwych par walutowych
        #"""
        return self._Request('get','/products')
    def _Request(self, method ,endpoint, params=None, data=None):
        #"""
        #Wysy�a zapytanie do strony. Po doj�ciu do tego momentu nast�pi wyj�cie z klasy

        #    Wej�cie:
        #            method (str):   Metoda HTTP (get, post, delete)
        #            endpoint (str): ko�c�wka adresu HTTP odpowiednia do zapytania
        #            params (dict):  dodatkowe parametry do zapytania HTTP (opcionalne)
        #            data (str):     parametry w formacie JSON do zapytania HTTP typu POST (opcionalne)
        #    Wyj�cie:
        #            odpowiedz w formacie JSON (list/dict)
        #"""
        url=self.url+endpoint
        r=self.session.request(method, url, params=params, data=data, auth=self.auth, timeout=30)
        return r.json()

P_Re=Public_Requester()
respond=P_Re.Produkty()
print(json.dumps(respond, indent=4))