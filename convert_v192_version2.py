# Author  : 
# Created :
# modified by for user interface
import glob
import pandas as pd
from tkinter import filedialog
import os

fname= filedialog.askopenfilename(title='Select a Dat file which you want to convert to v18')

print(fname)

fname = glob.glob("*.dat")[0]
if fname == []:

    fname = glob.glob("*.inp")[0]
mylines = []
with open (fname, 'rt') as myfile:
    for myline in myfile:
        mylines.append(myline.rstrip('\n'))

fname = glob.glob("*.dat")[0]
if fname == []:
    fname = glob.glob("*.inp")[0]
mylines = []
with open (fname, 'rt') as myfile:
    for myline in myfile:
        mylines.append(myline.rstrip('\n'))

lbl1 = []
for myline in mylines:
    if '/com,******************* SOLVE FOR LS' in myline:
        lbl1.append(mylines.index(myline))

for x in range(1, len(lbl1)+1):
    if x != len(lbl1):
        globals()['solve_LS%s' % x] = mylines[lbl1[x-1]:lbl1[x]]
    else:
        globals()['solve_LS%s' % x] = mylines[lbl1[x-1]:]

lbl3 = []
for i in range(1, len(lbl1)+1):
    lbl2 = []
    for line in globals()['solve_LS%s' % i]:
        if ('bfblock,' in line) or ('bf,' in line):
            lbl2.append(globals()['solve_LS%s' % i].index(line))
    try:
        globals()['temp_LS%s' % i] = globals()['solve_LS%s' % i][lbl2[0]:lbl2[1]][2:]
        lbl3.append(i)
    except:
        pass

for i in range(1, len(lbl1)+1):
    try:
        for j in range(len(globals()['temp_LS%s' % i])):
            globals()['temp_LS%s' % i][j] = list(map(float, globals()['temp_LS%s' % i][j].split()))
        globals()['df_temp_LS%s' % i] = pd.DataFrame(globals()['temp_LS%s' % i], columns =['nn', 'x'])
        globals()['df_temp_LS%s' % i]['nn'] = globals()['df_temp_LS%s' % i]['nn'].astype('int')
    except:
        pass

for LS in lbl3:
    globals()['list_temp_LS%s' % LS] = [' ']*(len(globals()['df_temp_LS%s' % LS])+2)
    globals()['list_temp_LS%s' % LS][0] = '/nopr'
    for j in range(len(globals()['df_temp_LS%s' % LS])):
        globals()['list_temp_LS%s' % LS][j+1] = 'bf,' + str(globals()['df_temp_LS%s' % LS]['nn'][j]) + ',temp,' + str(globals()['df_temp_LS%s' % LS]['x'][j])
    globals()['list_temp_LS%s' % LS][-1] = '/gopr'
    with open('bf_temp_LS%s.inp' % LS, 'w') as f:
        f.write('\n'.join(globals()['list_temp_LS%s' % LS]))

temp_list = [i for i, e in enumerate(mylines) if e == 'bf,end,loc,-1,']
for i in range(len(lbl3)):
    mylines.insert(temp_list[i]+i+2, '/input,bf_temp_LS'+str(lbl3[i])+',inp')

mylines = [myline.replace('MP,UVID','!MP,UVID') for myline in mylines]
nfname = os.path.basename(fname)
with open(nfname.split('.')[0]+'_v192.dat', 'w') as f:
    f.write('\n'.join(mylines))