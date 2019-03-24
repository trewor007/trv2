start=1542597000.0
end=1542893400.0
x=300
skala=900
if (int(end)-int(start)) > (x*int(skala)):
    end_tmp=end
    end=start+(x*skala)
    print("a")
    while end < end_tmp:
        start=end
        end=start+(x*skala)
        print('b')
    else:
        end=end_tmp
        print('c')
else:
    print('d')
