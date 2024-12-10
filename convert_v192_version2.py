#created on 30th Nov 2024
"""
this macro is used to convert Ansys dat file from higher version 2020 onwards into lower version 19.
do sanity check with the number of load cases and number of nodes after the conversion is done for verification.
only the temperature and material format is taken care here, if any changes obseved report it and macke modification to
this macro as required.
"""

import glob
import pandas as pd
from collections import defaultdict
word_indices = defaultdict(list)
from tkinter import filedialog
import os

fname= filedialog.askopenfilename(title='Select a Dat file which you want to convert to v18')

print(fname)
#fname = glob.glob("*.dat")[0]
#print(fname)
if fname == []:
    fname = glob.glob("*.inp")[0]
    print(fname)
mylines = []
with open (fname, 'rt') as myfile:
    for myline in myfile:
        mylines.append(myline.rstrip('\n'))
myfile.close()

lbl1 = []
for myline in mylines:
    if '/com,******************* SOLVE FOR LS' in myline:
        lbl1.append(mylines.index(myline))

print('Load case line index numbers:', lbl1)

for x in range(1, len(lbl1)+1):
    if x != len(lbl1):
        globals()['solve_LS%s' % x] = mylines[lbl1[x-1]:lbl1[x]]
    else:
        globals()['solve_LS%s' % x] = mylines[lbl1[x-1]:]
with open('solve_Loadstep.txt', 'w+') as f:
    # write elements of list
    for items in solve_LS2:
        f.write('%s\n' % items)
f.close()

lbl3 = []
LS1=[]
for i in range(1, len(lbl1)+1):
    lbl2 = []
    for line_index, line in enumerate(globals()['solve_LS%s' % i],start=1):
        words = line.strip().split(",")
        for word in words:
            #print(word)
            if word == 'bfblock' or word == 'bf':
                lbl2.append(line_index)
                print("printing line index:",line_index)
                print("printing lbl2:",lbl2)
                #lbl2.append(globals()['solve_LS%s' % i].index(word_indices['bfblock']))
        #if ('bfblock,' in line) or ('bf,' in line):
            if word == 'bfblock':
                LS1.append(i)
            #lbl2.append(globals()['solve_LS%s' % i].index(line))
    """  here the user needs to modify the code according to his temperature import data. if only one import thermal file
        is used then lbl2[0]:lbl2[1] is used, if two import thermal file used then lbl2[0],lbl2[1] ,lbl2[2],lbl2[3]  is used
        and so on... and add all these values.
        accordingly modify the below code
       """
    print("printing loadcase:",LS1)
    try:

        globals()['temp_LS%s' % i] = globals()['solve_LS%s' % i][lbl2[0]:lbl2[1]][1:-1]
                                     #globals()['solve_LS%s' % i][lbl2[2]:lbl2[3]][1:-1]+\
                                     #globals()['solve_LS%s' % i][lbl2[4]:lbl2[5]][1:-1]

        lbl3.append(i)

        print('try block lbl3', lbl3)
        print('LS index', lbl1)
        print('try block lbl2',lbl2)
    except:
        pass
"""with open('temps_check.txt', 'w+') as f:
    # write elements of list
    for items in temp_LS2:
        f.write('%s\n' % items)
f.close()"""

for i in range(1, len(lbl1)+1):
    try:
        print('entering %s loop start' %i)
        print(len(globals()['temp_LS%s' % i]))
        for j in range(len(globals()['temp_LS%s' % i])):
            globals()['temp_LS%s' % i][j] = list(map(float, globals()['temp_LS%s' % i][j].split()))
        globals()['df_temp_LS%s' % i] = pd.DataFrame(globals()['temp_LS%s' % i], columns =['nn', 'x'])

        globals()['df_temp_LS%s' % i]['nn'] = globals()['df_temp_LS%s' % i]['nn'].astype('int')
        print('entering %s loop end' %i)
    except:
        pass

"""with open('df_check.txt', 'w+') as f:
    # write elements of list
    for items in df_temp_LS4:
        f.write('%s\n' % items)
f.close()"""

for LS in lbl3:
    globals()['list_temp_LS%s' % LS] = [' ']*(len(globals()['df_temp_LS%s' % LS])+2)
    globals()['list_temp_LS%s' % LS][0] = '/nopr'
    for j in range(len(globals()['df_temp_LS%s' % LS])):
        globals()['list_temp_LS%s' % LS][j+1] = 'bf,' + str(globals()['df_temp_LS%s' % LS]['nn'][j]) + ',temp,' + str(globals()['df_temp_LS%s' % LS]['x'][j])
    globals()['list_temp_LS%s' % LS][-1] = '/gopr'
    with open('bf_temperature_LS%s.inp' % LS, 'w') as f1:
        f1.write('\n'.join(globals()['list_temp_LS%s' % LS]))
    f1.close()

temp_list = [i for i, e in enumerate(mylines) if e == 'bf,end,loc,-1,']
print("end of bf,end:", temp_list)

for i in range(len(lbl3)):
    mylines.insert(temp_list[i]+i+2, '/input,bf_temperature_LS'+str(lbl3[i])+',inp')

mylines = [myline.replace('MP,UVID','!MP,UVID') for myline in mylines]
mylines = [myline.replace('MP,UMID','!MP,UMID') for myline in mylines]
with open(fname.split('.')[0]+'_v192.dat', 'w') as f:
    f.write('\n'.join(mylines))
print('File creation completed!')

# below section to get the index value of bfblock and remove it from the input file and save as to file.
l2rm = []
global temp_file
for line_index, line in enumerate(mylines ,start=1):
    words = line.strip().split(",")
    for word in words:
        #print(word)
        if word == 'bfblock' or word == 'bf':
            l2rm.append(line_index)
            print("printing line index:",line_index)
            print("printing lbl2:",l2rm)
try:
    temp_file =mylines[0:l2rm[0]-1]+\
               mylines[l2rm[1]+1:l2rm[2]-1]+\
               mylines[l2rm[3]+1:]
except:
    pass
with open(fname.split('.')[0]+'_v192_updated.dat', 'w') as f:
    f.write('\n'.join(temp_file ))
#print(temp_file)

# check the link: https://ansysdat-converter.onrender.com
