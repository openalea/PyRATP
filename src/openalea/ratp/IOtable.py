""" Input/output functions for tables in csv or txt format.
This module may be rewrite for efficiency using pandas library.
"""

from os.path import join

def N_lignes (fichier) :
    """Count the number of lines in a file without changing the file pointer position"""

    position_ini = fichier.tell()
    fichier.seek(0)
    N_tot_lignes = len (fichier.readlines())
    fichier.seek(position_ini)
    return N_tot_lignes

def transcript_csv_str (fichier) :
     """ Convert a line of csv into a list of float """
     ligne_ch = fichier.readline()
     liste, i, caract = [], 0, '' #init a empty list and an index at 0 and an empty string 

     if ligne_ch == '' : #check if the string is empty
         return 'chaine vide'
   
     while ligne_ch[i] !=  '\n': #loop for a value in .csv (separator ;)
         ch = ligne_ch[i]
         if ligne_ch[i] == ',' : #convert decimal separator into point
            ch = '.'
         if ligne_ch[i] == ';'  :
            liste.append (caract)
            caract = ''
         if ligne_ch[i] != ';' :
            caract = caract + ch
         i=i+1

     liste.append(caract) # add the last value
     return liste

def table_csv_str (fichier) :
    """transcribe a .csv file of strings into a table (list of list) of strings """

    fichier.seek(0)
    liste, n = [], N_lignes(fichier)
    
    for i in range(n) :
        liste.append (transcript_csv_str (fichier))

    return liste

def transcript_csv (fichier) :
     """ Convert a line of csv into a list of float """
     ligne_ch = fichier.readline()
     liste, i, caract = [], 0, '' 
     if ligne_ch == '' : #check if the string is empty
         return 'chaine vide'
   
     while ligne_ch[i] !=  '\n': #loop for a value in .csv (separator ;)
         ch = ligne_ch[i]
         if ligne_ch[i] == ',' : #convert decimal separator into point
            ch = '.'
         if ligne_ch[i] == ';'  :
            liste.append (float(caract))
            caract = ''
         if ligne_ch[i] != ';' :
            caract = caract + ch
         i=i+1

     liste.append (float(caract)) # add the last value

     return liste

def table_csv (fichier) :
    """transcribe a .csv file into a table (list of list) of floats """

    fichier.seek(0)
    liste, n = [], N_lignes(fichier)
    
    for i in range(n) :
        liste.append (transcript_csv (fichier))

    return liste

def transcript_txt (fichier) :
     """ Convert a line of txt into a list of strings """
     ligne_ch = fichier.readline()
     liste, i, caract = [], 0, '' 
     if ligne_ch == '' : 
         return 'chaine vide'
   
     while ligne_ch[i] !=  '\n': 
         ch = ligne_ch[i]
         if (ligne_ch[i] == ' ' or ligne_ch[i] == "\t") and caract != '' :
            liste.append (caract)
            caract = ''
         if ligne_ch[i] != ' ' and ligne_ch[i] != "\t":
            caract = caract + ch
         i=i+1

     liste.append (caract) 
     return liste


def table_txt (fichier) :
    """transcribe a .txt file into a table (list of list) of strings """

    fichier.seek(0)
    liste, n = [], N_lignes(fichier)
    
    for i in range(n) :
        liste.append (transcript_txt (fichier))

    return liste

def ecriture_csv (table, fichier) :
    """ write table (list of list) of numbers into a csv file """
    for i in range (len(table)):
        for j in range (len(table[i][0:])-1) :
            fichier.write(str(table[i][j]))
            fichier.write(';')
        fichier.write(str(table[i][j+1]))
        fichier.write('\n')
    fichier.close()

def ecriture_txt (table, fichier) :
    """ write table (list of list) of numbers into a txt file """
    for i in range (len(table)):
        for j in range (len(table[i][0:])-1) :
            fichier.write(str(table[i][j]))
            fichier.write(' ')
        fichier.write(str(table[i][j+1]))
        fichier.write('\n')
    fichier.close()

def copie_partielle (fichier,out,n,m):
    """ copy lines from n to m from fichier to out """
    for i in range(m):
        ligne_ch = fichier.readline()
        if i>=n:
            out.writelines(ligne_ch)


def conv_dataframe(tab):
    """ convert list of list into dictionary of lists  with 1st row as key. 
    Format compatible for R DataFrame
    """
    dat = {}
    for i in range(len(tab)):
        dat[str(tab[i][0])] = tab[i][1:]

    return dat #r.as_data_frame(dat)

def conv_list(tab):
    """ convert dictionary of lists into list of lists with key as first element of each list
    
    Format compatible for my_csv
    """
    dat = []
    for i in tab.keys():
        v = [i]
        dat.append(v)

    count = 0
    for i in tab.keys():
        for j in range(len(tab[i])):
            dat[count].append(tab[i][j])

        count = count+1

    return dat 

def extract_dataframe(dat, ls_cles, cle, val=None, oper='egal'):
    """ extract from dat (dictionary of lists) a sub-dictionary where dat[cle] respect cle  ival  val  
    option oper : 'egal', 'inf', 'sup', 'infeg', 'supeg', 'diff'
    """
    
    #create list of index or cle = val

    id = []
    for i in range(len(dat[cle])):
        if val == None:
            id.append(i)
        else:
            if oper =='egal':
                if dat[cle][i] == val:
                    id.append(i)
            elif oper =='inf':
                if dat[cle][i] < val:
                    id.append(i)
            elif oper =='sup':
                if dat[cle][i] > val:
                    id.append(i)
            elif oper =='infeg':
                if dat[cle][i] <= val:
                    id.append(i)
            elif oper =='supeg':
                if dat[cle][i] >= val:
                    id.append(i)
            elif oper =='diff':
                if dat[cle][i] != val:
                    id.append(i)

    x = {}
    for k in ls_cles: 
        v = []
        for i in id: 
            v.append(dat[k][i])

        x[k] = v

    return x
    #extract_dataframe(dat, cles, 'geno', geno)
    #extract_dataframe(dat, cles, 'geno')

def t_list(tab):
    """transpose tab"""
    res = []
    for j in range(len(tab[0])):
        v = []
        for i in range(len(tab)):
            v.append(tab[i][j])
        
        res.append(v)

    return res


def conv_list2(tab):
    """ convert dictionary into list of lists with key as first element of each list"""
    dat = []
    for i in tab.keys():
        v = [i, tab[i]]
        dat.append(v)
    
    return dat 


def write_dict(dict, directory, name):

    try:
        tab = t_list(conv_list(dict))
    except:
        tab = conv_list2(dict)

    out = file(join(directory, name), 'w')
    ecriture_csv (tab, out)  
    out.close()
    return join(directory, name)

