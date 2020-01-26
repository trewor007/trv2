Asks=[['166.91','38'], ['166.87','12'], ['167.38', '90']]
aktualizacja=[  {"changes": [["buy", "166.10", "22.11000000"]]}]

a=[[2,4], [3,6], [6,8], [10,10]]
b=[[10,1],[8,3], [6,5], [2,9]]
call=[11,1]
d=False
for c in a:
    print(c)
    if call[0] == c[0]:
        print(c, 'yes')
        d=True
        break                   #jak potem będą problemy to pewnie dlatego
    else:
        print(c, 'no')
if d==False:
    print("dodajemy")
    for num, e in enumerate(a):
        print(num, e)
        if call[0]<e[0]:
            a.insert(num,call)
            break
        elif num==(len(a)-1):
            a.append(call)
            break
        else:
            pass
if d==False:
    print("Odejmujemy")
    for num, e in enumerate(b):
        print(num, e)
        if call[0]>e[0]:
            b.insert(num,call)
            break
        elif num==(len(b)-1):
            b.append(call)
            break
        else:
            pass

print(a)
print(b)

#res=any(b[0] in sub for sub in a)
#print(res)



