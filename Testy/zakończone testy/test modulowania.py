a=[[0] for _ in range(4)]
b=[[0] for _ in range(4)]
c=[[1] for _ in range(4)]

print(a, b, c)

class zupa():
    def barszcz(self, a, b, c, x):
        a[x]=a[x]+b[x]
        b[x]=b[x]+c[x]
        c[x]=c[x]+a[x]
        return a, b, c

zu=zupa()

x=1
zu.barszcz(a, b, c, x)
print(a, b, c)
print('\n')

x=0
zu.barszcz(a, b, c, x)
print(a, b, c )
print('\n')

x=3
zu.barszcz(a, b, c, x)
print(a, b, c )
print('\n')
