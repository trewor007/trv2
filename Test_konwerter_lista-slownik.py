a=[['a','1'],['b','2'],['c','3'],['d','4']]
b=[['e','5'],['f','6'],['g','7']]

def Konwerter1(lista):
    '''Zamiana listę list na jeden słownik.
     Pierwszy element każdej zagnieżdzonej listy staje się kluczem słownika.
     Drugi element jako lista staje się wartośćią klucza.
     ''' 
    Konwersja={d[0]: d[1:] for d in lista}
    return Konwersja
def Konwerter(lista):
    '''Zamiana listę list na jeden słownik.
     Pierwszy element każdej zagnieżdzonej listy staje się kluczem słownika.
     Drugi element zostaje wyciągnięty z listy i staje się wartośćią klucza.
     ''' 
    Konwersja={d[0]: ' '.join(d[1:]) for d in lista}   
    return Konwersja
print('Wejście:')
print(a)
print(b)
print('Wyjście:')
print('Konwerter1:',Konwerter1(a))
print('Konwerter2:',Konwerter(a))
