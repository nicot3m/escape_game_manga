"""
Escape game manga v1
Auteur: nicot3m
Date: 3/12/2020
Jeu d'évasion avec quizz thème manga
Le personnage se déplace grâce aux flèches de direction.
Des indices sont cachés dans les objets.
Les réponses aux questions permettent d'ouvrir les portes.
Il faut ramasser tous les objets pour ouvrir la porte de sortie.
Entrées:
         Le fichiers plan_chateau_manga.txt
         Le fichier dico_objets_manga.txt
         Le fichier dico_portes_manga.txt
         Les flèches de direction.
         Les réponses aux questions.
Sorties:
         Le plan du château dans une fenêtre turtle.
         Les mouvements du personnage.
         L'inventaire.
         Les question et l'ouverture des portes.         
"""

#import des modules

import turtle


# Définition des constantes globales

from CONFIGS import *


# Définition des fonctions

#niveau 1: Construction et affichage du plan du château

def lire_matrice(fichier):
    """
    Lecture de fichier et création de la matrice mat avec les éléments de fichier.
    Dans ce programme, un élément correspond à une case.
    mat[i][j]=k désigne les numéros de ligne et de colonne de cette case.
    k peut prendre la valeur:
    0 pour une case vide,
    1 pour un mur (infranchissable),
    2 pour la case de sortie/victoire,
    3 pour une porte qui sera franchissable en répondant à une question,
    4 pour une case contenant un objet à collecter.
    Entrée: fichier
    Résultat: mat
    """
    matrice=[]
    with open(fichier,"r") as mon_fichier:
        for ligne in mon_fichier:
            ligne=ligne.split() #Convertit une ligne de fichier en liste d'éléments entre espaces.
            for j in range(len(ligne)):
                ligne[j]=int(ligne[j])
            matrice.append(ligne)
    return matrice


def calculer_pas(matrice):
    """
    Calcule la taille en pixels (pas) d'une case du plan définie dans matrice.
    Toutes les cases ont la même taille.
    Entrée: matrice
    Résultat: pas
    """
    largeur_plan=ZONE_PLAN_MAXI[0]-ZONE_PLAN_MINI[0] #largeur du plan maxi en pixels
    hauteur_plan=ZONE_PLAN_MAXI[1]-ZONE_PLAN_MINI[1] #hauteur du plan maxi en pixels
    pas_largeur=largeur_plan//len(matrice[1]) #pas maxi pour la largeur
    pas_hauteur=hauteur_plan//len(matrice) #pas maxi pour la hauteur
    pas=min(pas_largeur,pas_hauteur)
    return pas


def coordonnees(case, pas):
    """
    Calcule les coordonnées x et y du coin inférieur gauche d'une case du plan
    en fonction des numéros de ligne et de colonne de la case et du pas. 
    Entrées: case, pas
    Résultat: coord_case
    """
    x_case=ZONE_PLAN_MINI[0]+case[1]*pas
    y_case=ZONE_PLAN_MAXI[1]-(case[0]+1)*pas
    coord_case=(x_case,y_case)
    return coord_case


def tracer_carre(pas):
    """
    Trace un carré de taille pas.
    Entrée: pas
    Résultat: Tracé d'un carré dans turtle
    """
    
    turtle.begin_fill()
    for i in range(4):
        turtle.forward(pas)
        turtle.left(90)
    turtle.end_fill()


def tracer_case(case, couleur, pas):
    """
    Calcule la position du coin inférieur gauche de la case à l'aide de la fonction coordonnees
    et y trace une case carrée de dimension pas et de couleur à l'aide de la fonction tracer_carre.
    Entrée: case, couleur, pas
    Résultat: Tracé dans turtle
    """
    coord_case=coordonnees(case, pas)
    turtle.up()
    turtle.color(couleur)
    turtle.goto(coord_case[0],coord_case[1])
    tracer_carre(pas)


def titre_inventaire():
    """
    Ecrit le tritre de l'inventaire
    Entrée: N/A
    Sortie: Ecrit dans turtle
    """
    turtle.goto(POINT_AFFICHAGE_INVENTAIRE)
    turtle.color("black")
    turtle.write("Inventaire :",font=("Arial", 8,'bold'))


def afficher_plan(matrice,pas):
    """
    Trace les cases du plan dans turtle avec la fonction tracer_case.
    Appelle la fonction titre_inventaire.
    Entrée: matrice
    Résultat: Tracé du plan dans turtle
    """
    turtle.hideturtle()
    turtle.speed(0) #Vitesse maxi de la tortue
    turtle.tracer(0) #Affichage non mis à jour pour accélérer le tracé.
    turtle.bgcolor(COULEUR_EXTERIEUR) #Définit la couleur de fond de la fenêtre turtle
    for i, line in enumerate(matrice):
        for j, col in enumerate(line):
            couleur_case=COULEURS[col] #Définit la couleur de la case
            case_ij=(i,j)
            tracer_case(case_ij, couleur_case, pas) #Trace la case
    titre_inventaire()
    turtle.tracer(1) #Mise à jour affichage


#niveau 2 : gestion des déplacements

#Trace personnage dans turtle
tracer_perso=lambda pas:turtle.dot(pas*RATIO_PERSONNAGE,COULEUR_PERSONNAGE)


def tracer_carre_vu(pas):
    """
    Trace un carré de taille pas à l'aide de la fonction tracer_carre
    pour indiquer que le personnage y est déjà passé.
    Entrée: pas
    Résultat: Tracé d'un carré dans turtle
    """
    turtle.color(COULEURS[5]) #Couleur de case vue
    #Positionne la tortue au coin inférieur gauche de la case.
    turtle.goto(turtle.pos()[0]-pas/2,turtle.pos()[1]-pas/2) 
    tracer_carre(pas)
    #Repositionne la tortue au centre de la case.
    turtle.goto(turtle.pos()[0]+pas/2,turtle.pos()[1]+pas/2) 


def deplacer_couloir(mouvement,position):
    """
    Trace un carré de taille pas à l'aide de la fonction tracer_perso
    pour indiquer que le personnage y est déjà passé.
    Entrée: pas
    Résultat: Tracé d'un carré dans turtle
    """    
    tracer_carre_vu(pas_case)
    #Met la tortue à la case suivante
    turtle.goto(turtle.pos()[0]+pas_case*mouvement[1],turtle.pos()[1]-pas_case*mouvement[0])
    tracer_perso(pas_case) #Trace personnage dans turtle
    position=(position[0]+mouvement[0],position[1]+mouvement[1])
    return position


def deplacer(mouvement):
    """
    Effectue une action à l'aide des fonctions suivantes:
    deplacer_couloir
    poser_question
    ramasser_objet
    porte_sortie
    en fonction du mouvement et de la case connexe.
    Entrée: mouvement + global position case et matrices_cases
    Résultat: Tracé d'un carré dans turtle
    """
    global position_case, matrice_cases
    
    turtle.onkeypress(None, "Left") # Désactive la touche Left
    turtle.onkeypress(None, "Right") # Désactive la touche Right
    turtle.onkeypress(None, "Up") # Désactive la touche Up
    turtle.onkeypress(None, "Down") # Désactive la touche Down
    
    if matrice_cases[position_case[0]+mouvement[0]][position_case[1]+mouvement[1]]==0:
        turtle.tracer(0) #Affichage non mis à jour pour accélérer le tracé.
        position_case=deplacer_couloir(mouvement,position_case)
        turtle.tracer(1) #Mise à jour affichage
    elif matrice_cases[position_case[0]+mouvement[0]][position_case[1]+mouvement[1]]==3:
        position_case,matrice_cases=poser_question(mouvement,position_case,matrice_cases)
    elif matrice_cases[position_case[0]+mouvement[0]][position_case[1]+mouvement[1]]==4:
        position_case,matrice_cases=ramasser_objet(mouvement,position_case,matrice_cases)
    elif matrice_cases[position_case[0]+mouvement[0]][position_case[1]+mouvement[1]]==2:
        position_case=porte_sortie(mouvement,position_case)

    turtle.onkeypress(deplacer_gauche, "Left") # Réassocie la touche Left à la fonction deplacer_gauche
    turtle.onkeypress(deplacer_droite, "Right") # Réassocie la touche Right à la fonction deplacer_droite
    turtle.onkeypress(deplacer_haut, "Up") # Réassocie la touche Up à la fonction deplacer_haut
    turtle.onkeypress(deplacer_bas, "Down") # Réassocie la touche Down à la fonction deplacer_bas
    
def deplacer_gauche():
    """
    Lance la fonction déplacer.
    Entrée: touche clavier gauche
    Résultat: lance la fonction déplacer avec le paramètre mouvement_gauche
    """
    mouvement_gauche=(0,-1)
    deplacer(mouvement_gauche)


def deplacer_droite():
    """
    Lance la fonction déplacer.
    Entrée: touche clavier droite
    Résultat: lance la fonction déplacer avec le paramètre mouvement_droite
    """
    mouvement_droite=(0,1)
    deplacer(mouvement_droite)


def deplacer_haut():
    """
    Lance la fonction déplacer.
    Entrée: touche clavier haut
    Résultat: lance la fonction déplacer avec le paramètre mouvement_haut
    """
    mouvement_haut=(-1,0)
    deplacer(mouvement_haut)


def deplacer_bas():
    """
    Lance la fonction déplacer.
    Entrée: touche clavier bas
    Résultat: lance la fonction déplacer avec le paramètre mouvement_bas
    """
    mouvement_bas=(1,0)
    deplacer(mouvement_bas)


#niveau 3 : collecte d’objets dans le labyrinthe

def creer_dictionnaire_des_objets(fichier):
    """
    Crée un dictionnaire à partir des éléments de fichier.
    Entrée: fichier
    Résultat: dico
    """
    dico={}
    with open(fichier,"r",encoding="utf-8") as mon_fichier:
        for line in mon_fichier:
            clef,question=eval(line.strip())
            dico[clef]=question
    return dico


def effacer_message():
    """
    Trace un grand carré de COULEUR_EXTERIEUR pour effacer l'annonce.
    Entrée: N/A
    Résultat: tracé dans turtle
    """
    #Positionne la tortue en bas et à gauche du point d'affichage des annonces
    turtle.goto(POINT_AFFICHAGE_ANNONCES[0]-10,POINT_AFFICHAGE_ANNONCES[1]-10)
    turtle.color(COULEUR_EXTERIEUR,COULEUR_EXTERIEUR)
    turtle.begin_fill()
    for i in range(4): #Trace un carré de 800 de côté
        turtle.forward(800)
        turtle.left(90)
    turtle.end_fill()
    turtle.goto(POINT_AFFICHAGE_ANNONCES)
    turtle.color("black")


def transforme_case_suivante_en_couloir(pas,mouvement):
    """
    Trace un carré de COULEUR_COULOIR à la place de l'objet.
    Entrée: pas, mouvement
    Résultat: Tracé d'un carré dans turtle
    """
    coord_position=turtle.pos()
    #positionne la tortue au coin inférieur gauche de la case.
    turtle.goto(coord_position[0]-pas/2+pas*mouvement[1],coord_position[1]-pas/2-pas*mouvement[0]) 
    turtle.color(COULEURS[0])
    tracer_carre(pas)
    turtle.goto(coord_position)


def compte_objets(matrice):
    """
    Compte les objets à récolter.
    Entrée: marice
    Résultat: nombre_d_objets
    """
    nombre_d_objets=0
    for i in matrice:
        for j in i:
            if j==4: #Cherche 4 dans matrice
                nombre_d_objets+=1
    return nombre_d_objets


def ramasser_objet(mouvement,position,matrice):
    """
    Ramasse un objet, affiche une annonce et écrit dans inventaire à l'aide 
    des fonctions transforme_case_suivante_en_couloir, deplacer_couloir et effacer_message.
    Entrée: mouvement,position,matrice, global inventaire_objets
    Résultat: position,matrice, affichage dans turtle
    """    
    global inventaire_objets
    turtle.tracer(0) #Affichage non mis à jour pour accélérer le tracé.
    
    transforme_case_suivante_en_couloir(pas_case,mouvement) #Remplace l'objet par un couloir dans turtle
    position=deplacer_couloir(mouvement,position) #Le personnage avance sur la case de l'objet
    matrice[position[0]][position[1]]=0 #Remplace l'objet par un couloir dans matrice
    inventaire_objets|={str(dico_objets[position])} #Ajoute un objet dans inventaire
    coord_position=turtle.pos()
    
    effacer_message() #Efface l'annonce
    #Ecrit nouvelle annonce
    turtle.write("Vous avez trouvé un objet : "+str(dico_objets[position]),font=("Arial", 10,'bold'))
    
    turtle.goto(POINT_AFFICHAGE_INVENTAIRE[0],POINT_AFFICHAGE_INVENTAIRE[1]-len(inventaire_objets)*16)
    #Affiche le nouvel objet dans la zone inventaire de turtle 
    turtle.write("N° "+str(len(inventaire_objets))+" : "+str(dico_objets[position]),font=("Arial", 8,'bold'))
    turtle.goto(coord_position)
    
    turtle.tracer(1) #Mise à jour affichage
    return position,matrice


#Niveau 4 : le jeu escape game complet avec questions-réponses

def poser_question(mouvement,position,matrice):
    """
    Pose la question, ouvre la porte, affiche une annonce et écrit dans inventaire
    à l'aide des fonctions effacer_message et transforme_case_suivante_en_couloir.
    Entrée: mouvement,position,matrice
    Résultat: matrice, affichage dans turtle
    """    
    coord_position=turtle.pos()
    position_porte=(position[0]+mouvement[0],position[1]+mouvement[1])
    
    effacer_message() #Efface l'annonce
    turtle.write("Cette porte est fermée.",font=("Arial", 10,'bold')) #Ecrit nouvelle annonce
    
    reponse_joueur=turtle.textinput("Question",str(dico_questions[position_porte][0])) #Pose la question
    if reponse_joueur==None: #Si pas de réponse
        turtle.goto(coord_position)
    elif reponse_joueur.lower()==(dico_questions[position_porte][1]).lower(): #Si bonne réponse
        turtle.tracer(0) #Affichage non mis à jour pour accélérer le tracé.
        turtle.goto(coord_position)
        transforme_case_suivante_en_couloir(pas_case,mouvement) #Remplace la porte par un couloir dans turtle
        matrice[position_porte[0]][position_porte[1]]=0 #Remplace la porte par un couloir dans matrice
        
        effacer_message() #Efface l'annonce
        turtle.write("La porte s'ouvre!",font=("Arial", 10,'bold')) #Ecrit nouvelle annonce
        
        turtle.goto(coord_position)
        position=deplacer_couloir(mouvement,position) #Le personnage avance sur la case de la porte
        turtle.tracer(1) #Mise à jour affichage
    else: #Si réponse fausse
        effacer_message() #Efface l'annonce
        #Ecrit nouvelle annonce
        turtle.write("Ce n'est pas la bonne réponse, réessayez.",font=("Arial", 10,'bold'))
        turtle.goto(coord_position)
    
    turtle.listen() #Active le clavier
    return position,matrice


def porte_sortie(mouvement,position):
    """
    Si l'inventaire est complet, affiche une annonce puis place le personnage à la sortie
    à l'aide des fonctions tracer_carre_vu, tracer_perso et effacer_message.
    Entrée: mouvement,position,matrice
    Résultat: position, affichage dans turtle
    """
    turtle.tracer(0) #Affichage non mis à jour pour accélérer le tracé.
    if len(inventaire_objets)==nb_objets: #Si tous les objets sont ramassés.
        tracer_carre_vu(pas_case)
        turtle.goto(turtle.pos()[0]+pas_case*mouvement[1],turtle.pos()[1]-pas_case*mouvement[0])
        coord_position=turtle.pos()
        tracer_perso(pas_case) #Place le personnage à la sortie
        
        effacer_message() #Efface l'annonce
        turtle.color("red")
        turtle.write("Bravo, Vous avez gagné! \nVous pouvez quitter le jeu ou vous promener dans le labyrinthe.",
                     font=("Arial", 12,'bold')) #Ecrit nouvelle annonce
        
        turtle.goto(coord_position)
        position=(position[0]+mouvement[0],position[1]+mouvement[1])
    else: #S'il manque des objets.
        coord_position=turtle.pos()
        effacer_message() #Efface l'annonce
        #Ecrit nouvelle annonce
        turtle.write("Il faut d'abord ramasser tous les objets pour sortir.",font=("Arial", 10,'bold'))
        turtle.goto(coord_position) #Le personnage ne bouge pas.
    turtle.tracer(1) #Mise à jour affichage
    return position


# Code principal

inventaire_objets=set() #Crée l'ensemble vide inventaire_objets
matrice_cases=lire_matrice(fichier_plan) #Crée la matrice avec les cases du plan
pas_case=calculer_pas(matrice_cases) #Calcule le pas
nb_objets=compte_objets(matrice_cases) #Compte le nombre total d'objets dans le plan
dico_objets=creer_dictionnaire_des_objets(fichier_objets) #Crée un dictionnaire dico_objets
dico_questions=creer_dictionnaire_des_objets(fichier_questions) #Crée un dictionnaire dico_questions

afficher_plan(matrice_cases,pas_case) #Affiche le plan dans turtle
turtle.goto(coordonnees(POSITION_DEPART,pas_case)[0]+pas_case/2,\
coordonnees(POSITION_DEPART,pas_case)[1]+pas_case/2)
tracer_perso(pas_case) #Positionne personnage au départ
position_case=(POSITION_DEPART[0],POSITION_DEPART[1])

turtle.listen() # Déclenche l’écoute du clavier
turtle.onkeypress(deplacer_gauche, "Left") # Associe à la touche Left une fonction appelée deplacer_gauche
turtle.onkeypress(deplacer_droite, "Right") # Associe à la touche Right une fonction appelée deplacer_droite
turtle.onkeypress(deplacer_haut, "Up") # Associe à la touche Up une fonction appelée deplacer_haut
turtle.onkeypress(deplacer_bas, "Down") # Associe à la touche Down une fonction appelée deplacer_droite
turtle.mainloop() # Place le programme en position d’attente d’une action du joueur
