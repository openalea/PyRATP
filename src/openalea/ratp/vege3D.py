# Header
#

"""

"""
# Verifi? avec lecture de fichier vgx le 28/01/2011 MS certified
##from openalea.ratp import pyratp

from qtpy import QtCore
import random
#import pyRATP
import numpy as np
dicoMotCle = {}
dicoMotCle["Obj"] = 0
dicoMotCle["EchX"] = 0
dicoMotCle["EchY"] = 0
dicoMotCle["EchZ"] = 0
dicoMotCle["TransX"] = 0
dicoMotCle["TransY"] = 0
dicoMotCle["TransZ"] = 0
dicoMotCle["RotX"] = 0
dicoMotCle["RotY"] = 0
dicoMotCle["RotZ"] = 0
dicoMotCle["X1"] = 0
dicoMotCle["X2"] = 0
dicoMotCle["X3"] = 0
dicoMotCle["Y1"] = 0
dicoMotCle["Y2"] = 0
dicoMotCle["Y3"] = 0
dicoMotCle["Z1"] = 0
dicoMotCle["Z2"] = 0
dicoMotCle["Z3"] = 0
dicoMotCle["R"] = 0
dicoMotCle["G"] = 0
dicoMotCle["B"] = 0
dicoMotCle["VCmax"] = 0
dicoMotCle["ShootType"]=0
#'dicoMotCle["Vcmax"] = 0
dicoMotCle["TC"] = 0
dicoMotCle["Jmax"] = 0
dicoMotCle["Resp"] = 0
dicoMotCle["Pmax"] = 0
dicoMotCle["Alpha"] = 0
dicoMotCle["Teta"] = 0
dicoMotCle["Grp1"] = 0
dicoMotCle["Grp2"] = 0
dicoMotCle["Mask"] = 0
def dicoInit():
    for k in dicoMotCle.keys():
        dicoMotCle[k] = 0

class Vege3D(object):
    """
    """
    def __init__(self, *args, **kwds):
        """

        """
    @staticmethod

##    def readVGX(fileNameVGX,typeVege,bltypeVege=False,Azote=2):
    def readVGX(fileNameVGX,CoefAllo,typeVege=1,bltypeVege=True,Azote=2):
        nbLigne = 0
        """
        Reading a VegeSTAR (*.vgx) file and return 6 numpy arrays (type of vegetation, X, Y, Z, Leaf surface and Nitrogen 
        Input data ... VegeSTAR file
                   ... Allometric coefficient to get from leaf length the leaf surface area 
        Output data ... type of vegetation, X, Y, Z, Leaf surface and Nitrogen content 
        """
        #liste ? retourner
        tabTypeVege = np.array([])
        tabX =np.array([])
        tabY =np.array([])
        tabZ =np.array([])
        tabS =np.array([])
        tabN =np.array([])
        #lecture du fichier source
        file = QtCore.QFile(fileNameVGX)
        if not(file.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)):
            return
        textStream = QtCore.QTextStream (file)

        #recuperation de l'entete du fichier
        if not(textStream.atEnd()):
            entete = textStream.readLine()
        #a partir de l'entete, on recupere le numero de la colonne correspondant a chaque mot cle
        #- recherche du caractere de separation
        chrSeparation = ""
        for c in entete:
            if not (str(c).isalnum()):
                chrSeparation = str(c)
                break

        #- decoupage de la ligne d'entete
        listEntete = entete.split(chrSeparation)
        #- pour chaque mot cle, on verifie qu'il existe dans le dictionaire et on note son numero de colonne
        listEntete = list(listEntete)
        for mot in listEntete:
            if str(mot) in dicoMotCle:
                dicoMotCle[str(mot)] = listEntete.index(str(mot))+1
        nbObj=1

        while not(textStream.atEnd()):
            nbLigne +=1

            ligne = textStream.readLine().split(chrSeparation)

            nbObj += 1

            #transformation de la QStringList en liste python
            liste = []

            for ch in ligne :
                try:
                    val=float(ch)
                except ValueError:
                    print(ch,  " : valeur non numerique a la ligne : ", nbObj+1)
                    return
                liste.append(val)

            if bltypeVege :
                typeV = nbLigne -1
            else:
                typeV =  random.randint(0,typeVege-1)

            if  int(liste[listEntete.index("Obj")])>0:
                X = (liste[listEntete.index("TransX")])
                Y = (liste[listEntete.index("TransY")])
                Z = (liste[listEntete.index("TransZ")])
##                ShootType = (liste[listEntete.index("ShootType")])
##                ThermoC = (liste[listEntete.index("TC")])
                tabX= np.append(tabX,X)
                tabY= np.append(tabY,Y)
                tabZ= np.append(tabZ,Z)
                AREA = (liste[listEntete.index("EchX")])*(liste[listEntete.index("EchY")])*CoefAllo
            else:
                X1 = (liste[listEntete.index("X1")])
                Y1 = (liste[listEntete.index("Y1")])
                Z1 = (liste[listEntete.index("Z1")])
                X2 = (liste[listEntete.index("X2")])
                Y2 = (liste[listEntete.index("Y2")])
                Z2 = (liste[listEntete.index("Z2")])
                X3 = (liste[listEntete.index("X3")])
                Y3 = (liste[listEntete.index("Y3")])
                Z3 = (liste[listEntete.index("Z3")])
                tabX= np.append(tabX,(X1+X2+X3)/3.)
                tabY= np.append(tabY,(Y1+Y2+Y3)/3.)
                tabZ= np.append(tabZ,(Z1+Z2+Z3)/3.)
                tt01 = [X1-X2,Y1-Y2,Z1-Z2]
                tt02 = [X1-X3,Y1-Y3,Z1-Z3]
                CrossP = np.cross(tt01,tt02)
                AREA = 0.5*np.sum(np.abs(CrossP)**2)**(1./2)

            typeV =0
            #Entity numbers according to Aphis Pomi on shoots
##            if (ThermoC == 999): typeV = 1
            #Entity numbers set according to ShootType 01/2015 - Skip i.e typeV = 0
##            if (ShootType == 1.0): typeV =0
##            if (ShootType == 2.0): typeV =0
##            if (ShootType == 3.0): typeV =1
##            if (ShootType == 4.0): typeV =2
##            if (ShootType == 5.0): typeV =3
##            if (ShootType == 6.0): typeV =4
##            print(typeV =',typeV
##            typeV =0

            tabTypeVege= np.append(tabTypeVege,typeV)
            tabS= np.append(tabS,AREA)
            tabN= np.append(tabN,Azote)
##            print(Area',AREA
##            if nbLigne == typeVege : nbLigne=0
        file.close()
        print('VEGE3D OK')
        return (tabTypeVege,tabX,tabY,tabZ,tabS,tabN)



##if __name__ == "__main__":
##
##    sys.exit(app.exec_())