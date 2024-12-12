import json
from flask import Flask,render_template, request, jsonify, url_for,Response, redirect,send_file
import pandas as pd
from flask_cors import cross_origin
from flask_httpauth import HTTPBasicAuth
from io import BytesIO
from zipfile import ZipFile

import os
import glob
import shutil
app = Flask(__name__)
@app.route('/')
@app.route('/home')
@cross_origin()
def home_page():
        if request.authorization and request.authorization.username == 'username' and request.authorization.password =='hcl123!':
        return render_template('index1.html')

    return make_response('could not verify!',401,{'WWW-Authenticate':'Basic realm="Login Required"'})

    #return render_template('index1.html')

@app.route('/about')
def about():
    title= "About time point screening"
    return render_template('about.html', title=title)

@app.route('/clear_data',methods=['GET', 'POST'])
def clear_data():
    filepath = ('Static\Input.xlsx')
    filepath1 = ('Static\Temp.xlsx')
    if os.path.isfile(filepath):
        os.remove(filepath)
        comment =" file has been cleared"
    if os.path.isfile(filepath1):
        os.remove(filepath1)
        comment = "  Temp File has been cleared"
    else:
        comment = "     !!!! No file Exists"
    return render_template('download.html', clear_data=comment)

@app.route('/data', methods=['GET', 'POST'])
def data():
    if request.method == 'POST':
        try:

            #file = request.form['upload-file']
            file = request.files['upload-file']
            if not os.path.isdir('Static'):
                os.mkdir('Static')

            filepath1 = os.path.join('Static', file.filename)
            print(filepath1)
            if os.path.isfile(filepath1):
                os.remove(filepath1)
                print("source file is copied to dataframe and deleted")
            file.save(filepath1)
            #dest = os.path.join('Static' + 'worksheet.xlsx' )
            #os.rename(filepath1,dest)

            #data1 = pd.read_excel(file)

            #data1 = pd.read_excel(filepath1,sheet_name='Temp vs Time', skiprows = 3)
            #temp_data= pd.read_excel(filepath1,sheet_name='Temperature difference', skiprows = 1)
            fname =filepath1
            if fname == []:
                fname = glob.glob("*.inp")[0]
                print('fname is',fname)
            mylines = []
            with open(fname, 'rt') as myfile:
                for myline in myfile:
                    mylines.append(myline.rstrip('\n'))
            myfile.close()

            lbl1 = []
            for myline in mylines:
                if '/com,******************* SOLVE FOR LS' in myline:
                    lbl1.append(mylines.index(myline))

            print('Load case line index numbers:', lbl1)

            for x in range(1, len(lbl1) + 1):
                if x != len(lbl1):
                    globals()['solve_LS%s' % x] = mylines[lbl1[x - 1]:lbl1[x]]
                else:
                    globals()['solve_LS%s' % x] = mylines[lbl1[x - 1]:]

            lbl3 = []
            LS1 = []
            for i in range(1, len(lbl1) + 1):
                lbl2 = []
                for line_index, line in enumerate(globals()['solve_LS%s' % i], start=1):
                    words = line.strip().split(",")
                    for word in words:
                        # print(word)
                        if word == 'bfblock' or word == 'bf':
                            lbl2.append(line_index)
                            print("printing line index:", line_index)
                            print("printing lbl2:", lbl2)
                            # lbl2.append(globals()['solve_LS%s' % i].index(word_indices['bfblock']))
                        # if ('bfblock,' in line) or ('bf,' in line):
                        if word == 'bfblock':
                            LS1.append(i)
                        # lbl2.append(globals()['solve_LS%s' % i].index(line))
                """  here the user needs to modify the code accounding to his temperature import data. if only one import thermal file
                    is used then lbl2[0]:lbl2[1] is used if two import thermal file used then lbl2[0],lbl2[1] ,lbl2[2],lbl2[3]  is used
                    and so on... and add all these values.
                    accordingly modify the below code
                   """
                print("printing loadcase:", LS1)
                try:

                    globals()['temp_LS%s' % i] = globals()['solve_LS%s' % i][lbl2[0]:lbl2[1]][1:-1]
                                                 #globals()['solve_LS%s' % i][lbl2[2]:lbl2[3]][1:-1] + \
                                                 #globals()['solve_LS%s' % i][lbl2[4]:lbl2[5]][1:-1]

                    lbl3.append(i)

                    print('try block lbl3', lbl3)
                    print('LS index', lbl1)
                    print('try block lbl2', lbl2)
                except:
                    pass
            for i in range(1, len(lbl1) + 1):
                try:
                    print('entering %s loop start' % i)
                    print(len(globals()['temp_LS%s' % i]))
                    for j in range(len(globals()['temp_LS%s' % i])):
                        globals()['temp_LS%s' % i][j] = list(map(float, globals()['temp_LS%s' % i][j].split()))
                    globals()['df_temp_LS%s' % i] = pd.DataFrame(globals()['temp_LS%s' % i], columns=['nn', 'x'])

                    globals()['df_temp_LS%s' % i]['nn'] = globals()['df_temp_LS%s' % i]['nn'].astype('int')
                    print('entering %s loop end' % i)
                except:
                    pass
            filelist=[]
            for LS in lbl3:
                globals()['list_temp_LS%s' % LS] = [' '] * (len(globals()['df_temp_LS%s' % LS]) + 2)
                globals()['list_temp_LS%s' % LS][0] = '/nopr'
                for j in range(len(globals()['df_temp_LS%s' % LS])):
                    globals()['list_temp_LS%s' % LS][j + 1] = 'bf,' + str(
                        globals()['df_temp_LS%s' % LS]['nn'][j]) + ',temp,' + str(
                        globals()['df_temp_LS%s' % LS]['x'][j])
                globals()['list_temp_LS%s' % LS][-1] = '/gopr'
                with open('bf_temperature_LS%s.inp' % LS, 'w') as f1:
                    f1.write('\n'.join(globals()['list_temp_LS%s' % LS]))
                    filelist.append('bf_temperature_LS%s.inp' % LS)
                f1.close()

            temp_list = [i for i, e in enumerate(mylines) if e == 'bf,end,loc,-1,']
            print("end of bf,end:", temp_list)

            for i in range(len(lbl3)):
                mylines.insert(temp_list[i] + i + 2, '/input,bf_temperature_LS' + str(lbl3[i]) + ',inp')

            mylines = [myline.replace('MP,UVID', '!MP,UVID') for myline in mylines]
            mylines = [myline.replace('MP,UMID', '!MP,UMID') for myline in mylines]
            #with open(fname.split('.')[0] + '_v192.dat', 'w') as ff:
             #   ff.write('\n'.join(mylines))
            print('File creation completed!')

            # below section to get the index value of bfblock and remove it from the input file and save as to file.
            l2rm = []
            global temp_file
            for line_index, line in enumerate(mylines, start=1):
                words = line.strip().split(",")
                for word in words:
                    # print(word)
                    if word == 'bfblock' or word == 'bf':
                        l2rm.append(line_index)
                        print("printing line index:", line_index)
                        print("printing lbl2:", l2rm)
            try:
                temp_file = mylines[0:l2rm[0] - 1] + \
                            mylines[l2rm[1] + 1:l2rm[2] - 1] + \
                            mylines[l2rm[3] + 1:]
            except:
                pass
            fname1=os.path.splitext(os.path.basename(fname))[0]
            with open(fname1 + '_v192_updated.dat', 'w') as ff:
                ff.write('\n'.join(temp_file))
                filelist.append(fname1 + '_v192_updated.dat')

            os.remove(fname)

            stream = BytesIO()
            with ZipFile(stream, 'w') as zf:
                for fil in filelist:
                    zf.write(fil, os.path.basename(fil))
            stream.seek(0)
            for f in filelist:
                os.remove(f)
            return send_file(
                stream,
                as_attachment=True,
                download_name='archive.zip')

        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong in Interpolate module, check for input file'


if __name__   ==   '__main__':
    app.run(debug=True)
