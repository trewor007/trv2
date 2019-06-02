import pandas as pd

cena=[[[1,'00a', '00b', '00c'],[2,'01a','01b','01c'],[3,'02a','02b','02c']],
       [[1,'10a', '10b', '10c'],[2,'11a','11b','11c'],[3,'12a','12b','12c']],
       [[1,'20a', '20b', '20c'],[2,'21a','21b','21c'],[3,'22a','22b','22c']]]

produkty=['Aa','Bb','Cc']


"""
dla kazdego indeksu stworz tymczasowa baze danych i pobierz dane z listy.
następnie zmien nazwy kolumn tak by kazda z nich byla poprzedzona nazwa pary walutowej
ustaw czas jako indeks tabeli,    """
Main_data_frame=pd.DataFrame()                              #Tworzenie glownej bazy danych 
for produkt_id in range(len(produkty)): 
    data_frame=pd.DataFrame.from_records(cena[produkt_id], columns=['time', 'low_price', 'high_price', 'open_price'])
    data_frame.rename(columns={'low_price': f'{produkty[produkt_id]}_low_price',
                                'high_price': f'{produkty[produkt_id]}_high_price',
                                'open_price': f'{produkty[produkt_id]}_open_price',
                                'close_price': f'{produkty[produkt_id]}_close_price',
                                'volume': f'{produkty[produkt_id]}_volume'}, inplace=True) 
    data_frame.set_index('time', inplace=True)
    if len(Main_data_frame)==0:                             #pierwsza iteracja
        Main_data_frame=data_frame                          #glowna baza danych z tymczasowej bazy
    else:                                                   #kazda kolejna iteracja
        Main_data_frame=Main_data_frame.join(data_frame)    #tymczasowa baza danych doklejona z prawej strony glownej bazy danych
print(Main_data_frame.head())
Main_data_frame.shape()    



