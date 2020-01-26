def Konwerter(lista):
    '''Zamiana listę list na jeden słownik. Dla TypTranzakcji=="snapshot"
    Pierwszy element każdej zagnieżdzonej listy staje się kluczem słownika.
    Drugi element zostaje wyciągnięty z listy i staje się wartośćią klucza.
    ''' 
    Konwersja={d[0]: ' '.join(d[1:]) for d in lista}   
    return Konwersja