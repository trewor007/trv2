a=[[2,1], [4,3], [6,2], [8,5], [10,5]]
b=[[9,5],[7,5], [5,2], [3,3], [1,1]]
old_data=1
diff_alfa=0
diff_beta=0
for num, data in enumerate(a,1):
    if data[1]>old_data:
        print(num, data)
        diff_beta=data[1]-old_data
        if diff_beta>diff_alfa:
            diff_alfa=diff_beta
    old_data=data[1]
    print(num, data, old_data, diff_alfa, diff_beta)
    