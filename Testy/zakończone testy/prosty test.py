import json

""" First_Layer_Nods=   [5,6,16,32,64]
Second_Layer_Nods=  [8,16,32,64,128]
Third_Layer_Nods=   [8,16,32,64]
Forth_Layer_Nods=   [4,8,16,32]
Current_Layer_Nods= [0,0,0,0] """
First_Layer_Nods=   [17]
Second_Layer_Nods=  [8,17,32,64,128]
Third_Layer_Nods=   [8,17,32,64]
Forth_Layer_Nods=   [4,8,16,32]
Current_Layer_Nods= [0,0,0,0]
N=0

try:
    f= open("progress.txt", 'x')    #tworze plik zapisu postepu jezeli nie istnieje
except:
    with open('progress.txt') as fd:    #odczytuje zawartosc pliku jezli istnieje
        Current_Layer_Nods=json.load(fd)
print("Aktualne: {}".format(Current_Layer_Nods))
for First_Layer_Nod in First_Layer_Nods:
    if Current_Layer_Nods[0]<=First_Layer_Nod:
        for Second_Layer_Nod in Second_Layer_Nods:
            if Current_Layer_Nods[1]<=Second_Layer_Nod:
                if Second_Layer_Nod > First_Layer_Nod:
                    for Third_Layer_Nod in Third_Layer_Nods:
                        if Current_Layer_Nods[2]<=Third_Layer_Nod:
                            if Third_Layer_Nod <= Second_Layer_Nod:
                                for Forth_Layer_Nod in Forth_Layer_Nods:
                                    if Current_Layer_Nods[3]<Forth_Layer_Nod:
                                        if Forth_Layer_Nod <Third_Layer_Nod:
                                            N+=1
                                            print(N, First_Layer_Nod, Second_Layer_Nod, Third_Layer_Nod, Forth_Layer_Nod)
                                            sf=[First_Layer_Nod, Second_Layer_Nod, Third_Layer_Nod, Forth_Layer_Nod]
                                            #print(Current_Layer_Nods)
                                            with open('progress.txt','w') as outfile:
                                                json.dump(sf, outfile)
                                    if Current_Layer_Nods[3]==Forth_Layer_Nod and Current_Layer_Nods[2]==Third_Layer_Nod and Current_Layer_Nods[1]==Second_Layer_Nod and Current_Layer_Nods[0]==First_Layer_Nod and Current_Layer_Nods!=[0,0,0,0]:
                                        print("that one time")
                                        with open('progress.txt','w') as outfile:
                                            json.dump(sf, outfile)

    

