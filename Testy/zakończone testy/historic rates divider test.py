# This Python file uses the following encoding: utf-8
import base64
import datetime
import copy
import hmac
import h5py
import hashlib
import json
import platform
import urllib3
import urllib.request
import time
import timeit
import random
import queue

import threading as Thread
from Public_Requester import Public_Requester

#import Public_Requester as PR


produkty=['ETH-BTC']
produkt_id=0
cena=[[] for _ in range(len(produkty))]
def Preignitor():
    end=(time.time())
    start=end-880000
    for product_id in produkty:
        PR=Public_Requester()
        un_filtered=PR.Historic_rates_divider(start=start, end=end, skala=300, produkt=product_id)
        for v in range(len(un_filtered)):
            cena[produkty.index(product_id)].append(un_filtered[v])
Preignitor()






