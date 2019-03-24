product_id=0
cena=[[]]
while True:
    cena[product_id].append('0')
    if len(cena[product_id])>500:
        del cena[product_id][0]
    print(len(cena[product_id]))
