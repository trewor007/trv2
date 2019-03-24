zakres=[5,10,15,20]
produkty=['alfa',"beta","gamma","delta"]
print("-------------------------------------")
for produkt_id in range(len(produkty)):
    #print(smas[produkt_id][-1])
    print(produkt_id)
    print("===")
    for i in range(len(zakres)):
        print(produkt_id, i)
