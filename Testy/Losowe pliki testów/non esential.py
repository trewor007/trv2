"""
y=[1,5,7,3,7,89,5]
for x in range((len(y)+2)):
    print(x)
#x=x+1
#print(x)
"""
import time
import datetime
a="2018-12-01T18:02:16.661000Z"
#b=datetime.datetime.strptime(a, '%Y-%m-%dT%H:%M:%S.%fZ')
b=time.mktime(time.strptime(a, '%Y-%m-%dT%H:%M:%S.%fZ'))
print(b)
    
