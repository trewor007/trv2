import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

fig=plt.figure()
ax1=fig.add_subplot(1,1,1)
ax2=fig.add_subplot(1,1,1)

def animate(i):
    pullData=open('sampletxt.txt','r').read()
    dataArray=pullData.split('\n')
    xar=[]
    yar=[]
    yar2=[]    
    for eachLine in dataArray:
        if len(eachLine)>1:
            x,y,y1=eachLine.split(',')
            xar.append(int(x))
            yar.append(int(y))
            yar2.append(int(y1))
    ax1.clear()
    ax2.clear()
    ax1.plot(xar,yar)
    ax2.plot(xar,yar2)
ani=animation.FuncAnimation(fig,animate,interval=1000)
plt.show()
            
