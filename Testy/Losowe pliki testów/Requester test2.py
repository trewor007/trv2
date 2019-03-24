import json, hmac, hashlib, time, requests, base64
from requests.auth import AuthBase
from hashtag_generator import gdax_sandbox_key, gdax_sandbox_API_secret, gdax_sandbox_phassphrase

api_key=gdax_sandbox_key
secret_key=gdax_sandbox_API_secret
passphrase=gdax_sandbox_phassphrase

# Create custom authentication for Exchange
class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = signature.digest().encode('base64').rstrip('\n')

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request

api_url='https://public.sandbox.pro.coinbase.com'
auth = CoinbaseExchangeAuth(api_key, secret_key, passphrase)

# Get accounts
r = requests.get(api_url + 'accounts', auth=auth)
print(r.json())
# [{"id": "a1b2c3d4", "balance":...
