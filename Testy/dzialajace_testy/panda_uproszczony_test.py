import pandas as pd

cena=[[[1,'00a', '00b', '00c','00d','00e'],[2,'01a','01b','01c','01d','01e'],[3,'02a','02b','02c','02d','02e']],
       [[1,'10a', '10b', '10c','10d','10e'],[2,'11a','11b','11c','11d','11e'],[3,'12a','12b','12c','12d','12e']],
       [[1,'20a', '20b', '20c','20d','20e'],[2,'21a','21b','21c','21d','21e'],[3,'22a','22b','22c','22d','22e']]]

produkty=['Aa','Bb','Cc']


"""
dla kazdego indeksu stworz tymczasowa baze danych i pobierz dane z listy.
następnie zmien nazwy kolumn tak by kazda z nich byla poprzedzona nazwa pary walutowej
ustaw czas jako indeks tabeli,    """
Main_data_frame=pd.DataFrame()                              #Tworzenie glownej bazy danych 
for produkt_id in range(len(produkty)): 
    data_frame=pd.DataFrame.from_records(cena[produkt_id], columns=['time', 'low_price', 'high_price', 'open_price', 'close_price','volume'])
    data_frame.rename(columns={'low_price': f'{produkty[produkt_id]}_low_price',
                                'high_price': f'{produkty[produkt_id]}_high_price',
                                'open_price': f'{produkty[produkt_id]}_open_price',
                                'close_price': f'{produkty[produkt_id]}_close_price',
                                'volume': f'{produkty[produkt_id]}_volume'}, inplace=True)
    print(data_frame.head())
    if produkt_id != 0:
        data_frame.drop(columns=f'{produkty[produkt_id]}_volume', inplace=True)
        print(data_frame.head()) 
    data_frame.set_index('time', inplace=True)
    if len(Main_data_frame)==0:                             #pierwsza iteracja
        Main_data_frame=data_frame                          #glowna baza danych z tymczasowej bazy
    else:                                                   #kazda kolejna iteracja
        Main_data_frame=Main_data_frame.join(data_frame)    #tymczasowa baza danych doklejona z prawej strony glownej bazy danych
print(Main_data_frame.head())




