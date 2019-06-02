First_Layer_Nods=   [5,6,16,32,64]
Second_Layer_Nods=  [8,16,32,64,128]
Third_Layer_Nods=   [8,16,32,64]
Forth_Layer_Nods=   [4,8,16,32]
Current_Layer_Nods= [0,0,0,0]
N=0

for First_Layer_Nod in First_Layer_Nods:
    for Second_Layer_Nod in Second_Layer_Nods:
        if Second_Layer_Nod > First_Layer_Nod:
            for Third_Layer_Nod in Third_Layer_Nods:
                if Third_Layer_Nod <= Second_Layer_Nod:
                    for Forth_Layer_Nod in Forth_Layer_Nods:
                        if Forth_Layer_Nod <Third_Layer_Nod:
                            N+=1
                            print(N, First_Layer_Nod, Second_Layer_Nod, Third_Layer_Nod, Forth_Layer_Nod)
                            Current_Layer_Nods=[First_Layer_Nod, Second_Layer_Nod, Third_Layer_Nod, Forth_Layer_Nod]
                            print(Current_Layer_Nods)
                        else:
                            pass
                else:
                    pass
        else:
            pass
