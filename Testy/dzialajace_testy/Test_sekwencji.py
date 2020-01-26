# This Python file uses the following encoding: utf-8

import pandas as pd
import matplotlib.pyplot as plt

from Public_Requester import Public_Requester

produkty=["BTC-EUR"]
produkt_id=0
cena=[[] for _ in range(len(produkty))]
load_training_data=False
save_training_data=False

def Preignitor():

    start=1546297200
    end=1567814400#1560690848#1556372595
    for product_id in produkty:
        PR=Public_Requester()
        un_filtered=PR.Historic_rates_divider(start=start, end=end, skala=300, produkt=product_id)
        for v in range(len(un_filtered)):
            cena[produkty.index(product_id)].append(un_filtered[v])

Main_data_frame=pd.DataFrame()                              #Tworzenie glownej bazy danych 

if load_training_data==True:   #Odczyt z zapisanego pliku z danymi treningowymi
    Main_data_frame=pd.read_csv('Test_sekwencji_data.csv',sep=',')
    print("training data loaded from csv file")
else:
    Preignitor()
    """
    dla kazdego indeksu stworz tymczasowa baze danych i pobierz dane z listy.
    następnie zmien nazwy kolumn tak by kazda z nich byla poprzedzona nazwa pary walutowej
    ustaw czas jako indeks tabeli,    """
    
    for produkt_id in range(len(produkty)): 
        data_frame=pd.DataFrame.from_records(cena[produkt_id], columns=['time', 'low_price', 'high_price', 'open_price','close_price', 'volume'])

        """                 data_frame.rename(columns={'low_price': f'{produkty[produkt_id]}_low_price',
                                    'high_price': f'{produkty[produkt_id]}_high_price',
                                    'open_price': f'{produkty[produkt_id]}_open_price',
                                    'close_price': f'{produkty[produkt_id]}_close_price',
                                    'volume': f'{produkty[produkt_id]}_volume'}, inplace=True)  """

        data_frame.set_index('time', inplace=True)
        if len(Main_data_frame)==0:                             #pierwsza iteracja
            Main_data_frame=data_frame                          #glowna baza danych z tymczasowej bazy
        else:                                                   #kazda kolejna iteracja
            Main_data_frame=Main_data_frame.join(data_frame)    #tymczasowa baza danych doklejona z prawej strony glownej bazy danych
        print(Main_data_frame.head())
        if save_training_data==True:
            Main_data_frame.to_csv("Test_sekwencji_data.csv", index=True)
        else:
            pass



Main_data_frame=pd.read_csv('Test_sekwencji_data.csv',sep=',') #pobranie danych z pliku csv
Main_data_frame.set_index('time', inplace=True)

#Rozdzielanie bazy danych na dane treningowe, testowe i walidacyjne
times=sorted(Main_data_frame.index.values)
Train_data_frame_index=sorted(Main_data_frame.index.values)[int(0.6*len(times))]
Train_data_frame=Main_data_frame[(Main_data_frame.index<=Train_data_frame_index)]

Validation_data_frame_index=sorted(Main_data_frame.index.values)[int(0.80*len(times))]
Validation_data_frame=Main_data_frame[(Main_data_frame.index>=Train_data_frame_index)] 
Validation_data_frame=Validation_data_frame[(Validation_data_frame.index<=Validation_data_frame_index)]

Test_data_frame_index=sorted(Main_data_frame.index.values)[-int(0.20*len(times))]
Test_data_frame=Main_data_frame[(Main_data_frame.index>=Test_data_frame_index)]



MaDFP=Main_data_frame
TrDFP=Train_data_frame
VaDFP=Validation_data_frame
TeDFP=Test_data_frame
plt.plot(MaDFP['close_price'],'b', label='Main Data')
plt.plot(TrDFP['close_price'],'g', label='Train Data')
plt.plot(VaDFP['close_price'],'y', label='Validation Data')
plt.plot(TeDFP['close_price'],'r', label='Test Data')
plt.legend(loc='upper left')
plt.show()
blob=Train_data_frame.shape
print(blob)



