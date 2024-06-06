import IOtable
from scipy import array, absolute
import scipy

#scipy.dot -> produit scalaire
#scipy.cross -> produit vectoriel
def norme_v(vec):
    """ calcule la norme d'un vecteur """
    return scipy.sqrt((vec[2]*vec[2])+(vec[1]*vec[1])+(vec[0]*vec[0]))

def triangle_area(p1, p2, p3):
    """ compute surface area of a triangle """
    u = p2-p1
    v = p3-p1
    return absolute(0.5*norme_v(scipy.cross (u, v)[0]))

def tri_ortho(p1,p2,p3):
    """ compute  orthocenter of a triangle - meme resulat que .faceCenter(id) sur un triangle set"""
    #p4 milieu  p2-p3
    p4 = array(p2)+0.5*(array(p3)-array(p2))
    return array(p1)+2.*(p4-array(p1))/3.



def can2riri(can_file_path, Ncontent = 0.1):
    #open file
    f = file(can_file_path, 'r')
    tab_geom = IOtable.table_txt(f) 
    f.close()
    for i in range(1, len(tab_geom)-1):
        tab_geom[i][5:] = map(float, tab_geom[i][5:])

    tab = []
    for i in range(1, len(tab_geom)-1):
        #face center
        p1, p2, p3 = array([tab_geom[i][5:8]]), array([tab_geom[i][8:11]]), array([tab_geom[i][11:]])
        center = tri_ortho(p1,p2,p3)
        #triangle surface (m2)
        s = triangle_area(p1, p2, p3) 
        #elevation
        u = p2-p1
        v = p3-p1
        c = scipy.cross (u, v)[0]
        norm = c/norme_v(c)
        #id plante
        id = int(tab_geom[i][2][-3:])# va chercher dans les 3 derniers chiffres
        
        # sortie
        tab.append([id, center[0][0], center[0][1], center[0][2], s ])

    tab = IOtable.t_list(tab)
    entite, x, y, z, surf = tab[0], tab[1], tab[2], tab[3], tab[4]
    n = [Ncontent]*len(entite) #N fixe en entree
    entite = [0]*len(x) #pour forcer tout de la meme entite

    return array(entite), array(x)/100.+0.53, array(y)/100.+0.17, array(z)/100.+0.03, array(surf)/10000., array(n) #passe de cm2 en m2, cm en m #+ recale a l'origine [0,0,0]

#can_file_path = r'H:\devel\grass_plt.can'
#entite, x, y, z, surf, n = can2riri(can_file_path, Ncontent = 0.1)


#manque et angle pour calcul des k
#comment faire le lien avec les voxel pour la projection?
#tester avec les n plantes -> gestion des fichier param correspondant aux entites -> possibilite de pointer plusieurs fois vers le meme?
# pour boucler en diffus -> pas besoin de refaire ttes les heures??
# reprendre sans IOtable (read...)
#Rq: pour visu des sortie: isoler un t de simul : extract-time
#Rq 2: gestion du partage entre plantes pourrait etre gerer en post-traitement a partir des id can si peut faaire bijection entre triangles et rayonnement intercepter dans un voxel
#Rk: pour un voxel: attribue light sun - light-shade ou moyenne a un triangle -> regle?

#relatuion triangle - voxel a reconstruire a partir des coord initiale des objets
