import requests
import json
import hmac
import hashlib
import time
import base64
from requests.auth import AuthBase
from hashtag_generator import gdax_sandbox_key, gdax_sandbox_API_secret, gdax_sandbox_phassphrase

api_key=gdax_sandbox_key
secret_key=gdax_sandbox_API_secret
passphrase=gdax_sandbox_phassphrase
url='https://api-public.sandbox.pro.coinbase.com'



class CBProAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = ''.join([timestamp, request.method, request.path_url, (request.body or '')])
        request.headers.update(get_auth_headers(timestamp, message, self.api_key, self.secret_key, self.passphrase))
        return request
def get_auth_headers(timestamp, message, api_key, secret_key, passphrase):
    message = message.encode('ascii')
    hmac_key = base64.b64decode(secret_key)
    signature = hmac.new(hmac_key, message, hashlib.sha256)
    signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')
    return {
        'Content-Type': 'Application/JSON',
        'CB-ACCESS-SIGN': signature_b64,
        'CB-ACCESS-TIMESTAMP': timestamp,
        'CB-ACCESS-KEY': api_key,
        'CB-ACCESS-PASSPHRASE': passphrase
}


class Public_Requester():
    """
    Wszystkie zapytania niewymagające logowanie przesyłane są tą klasą
    """
    def __init__(self, url='https://public.sandbox.pro.coinbase.com', timeout=30, produkty='BTC-EUR', start=None, end=None, skala=None):
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

class Private_Requester(Public_Requester):
    """
    Wszystkie zapytania po zalogowaniu przesyłane są tą klasą(jeżeli w nawiasie powyżej jest "Public_Pequester" to zapytania z tej klasy są obsługiwane przez _Requester z tamtej klasy
    """
    def __init__(self, api_key, secret_key, passphrase, url='https://public.sandbox.pro.coinbase.com'):
        super(Private_Requester, self).__init__(url)
        self.auth=CBProAuth(api_key, secret_key, passphrase)
        self.session=requests.session()
    def get_konto(self, account_id):
        """
        Pobiera informacje na temat pojedyńczego konta

        Wejście:
                account_id (str): nazwa poszukiwanego konta
        Wyjście:
                Dane konta (dict)
        """
        return self._Request('get','/accounts/'+account_id)

    def get_konta(self):
        """
        jw tylko dla wielu
        """
        return self.get_konto('')
        
P_Re=Public_Requester(url='https://api-public.sandbox.pro.coinbase.com')
respond=P_Re.Produkty()
print(json.dumps(respond, indent=4))
pr=Private_Requester(api_key, secret_key, passphrase, url='https://api-public.sandbox.pro.coinbase.com')
a=pr.get_konta()
print(json.dumps(a, indent=4))
