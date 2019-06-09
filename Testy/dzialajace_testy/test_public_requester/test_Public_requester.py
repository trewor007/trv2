# This Python file uses the following encoding: utf-8

import pandas as pd
import matplotlib.pyplot as plt
from Public_Requester import Public_Requester

tryb=3

if tryb==1:
    #A B C
    end=    1546474200
    start=  1546297200

if tryb==2:
    #A C
    end=    1546374200
    start=  1546297200
if tryb==0:
    end=    1546344200
    start=  1546297200
if tryb==3:
    end=1556372595
    start=1546297200


produkty=['ETH-BTC']
produkt_id=0
cena=[[] for _ in range(len(produkty))]
Main_data_frame=pd.DataFrame() 
for product_id in produkty:
    PR=Public_Requester()
    un_filtered=PR.Historic_rates_divider(start=start, end=end, skala=300, produkt=product_id)
    for v in range(len(un_filtered)):
        cena[produkty.index(product_id)].append(un_filtered[v])

for produkt_id in range(len(produkty)): 
    data_frame=pd.DataFrame.from_records(cena[produkt_id], columns=['time', 'low_price', 'high_price', 'open_price','close_price', 'volume'])

    data_frame.set_index('time', inplace=True)
    if len(Main_data_frame)==0:                             #pierwsza iteracja
        Main_data_frame=data_frame                          #glowna baza danych z tymczasowej bazy
    else:                                                   #kazda kolejna iteracja
        Main_data_frame=Main_data_frame.join(data_frame)    #tymczasowa baza danych doklejona z prawej strony glownej bazy danych
    shape=Main_data_frame.shape
    print("{}".format(shape))
    print(Main_data_frame.head(137))


    Main_data_frame.to_csv("test_Public_request_data.csv", index=False)

MFDP=Main_data_frame
MFDP.plot(kind='line',y='close_price', use_index=True)
plt.show()


