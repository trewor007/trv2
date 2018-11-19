from matplotlib.pyplot import subplots, pause, show
from numpy import sin, pi

fig, ax = subplots()

x = [0]
y = [sin(2 * pi * x[-1])]
p1, = ax.plot(x, y) 

show(block = False)
while True:
    # update data
    x.append(x[-1] + .1)
    y.append(sin(2 * pi * x[-1]))
    p1.set_data(x, y) # update data
    ax.relim()        # rescale axis
    ax.autoscale_view()# update view
    pause(1e-3)
