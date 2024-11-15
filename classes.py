import random


class Game:
    def __init__(self):
        self.joueurs = []
        self.compteur_de_tour = 1
        self.joueur_qui_joue:int = None


    def ajouter_joueur(self, nom, couleur, drapeau=None):
        self.joueurs.append(Joueur(nom, couleur, drapeau))

    def ajouter_joueur_depuis_classe(self, joueur):
        self.joueurs.append(joueur)

    def initialisation(self, randomise_ordre=True):
        argent_options = [1000, 5000, 10000, 25000, 50000]
        population_options = [20, 50, 100, 250, 500]
        armée_options = [1, 2, 3, 4, 5]
        flotte_options = [1, 2, 3, 4, 5]
        territoire_options = (1000, 25000)
        if randomise_ordre:
            random.shuffle(self.joueurs)
        chance_points = 10
        for joueur in self.joueurs:
            random_argent_points = random.randint(0, min(chance_points, 4))
            chance_points -= random_argent_points
            random_argent = argent_options[random_argent_points]

            random_population_points = random.randint(0, min(chance_points, 4))
            chance_points -= random_population_points
            random_population = population_options[random_population_points]

            random_armée_points = random.randint(0, min(chance_points, 4))
            chance_points -= random_armée_points
            random_armée = armée_options[random_armée_points]

            random_flotte_points = random.randint(0, min(chance_points, 4))
            chance_points -= random_flotte_points
            random_flotte = flotte_options[random_flotte_points]

            random_taille_de_territoire = random.randint(*territoire_options)
            joueur.setup(random_argent, random_population, random_armée, random_flotte, random_taille_de_territoire)

class Map:
    pass


class Joueur:
    def __init__(self, nom, couleur, drapeau=None):
        self.nom = nom
        self.couleur = couleur
        self.drapeau = drapeau
        self.territoires = []
        self.argent = 0
        self.armée = 0
        self.flotte = 0
        self.population = 0
        self.infrastructures = []
        self.territoire_à_peindre_restant = 0

    def setup(self, argent, population, armée, flotte, taille_de_territoire):
        self.argent = argent
        self.armée = armée
        self.flotte = flotte
        self.population = population
        self.infrastructures = []
        self.territoire_à_peindre_restant = taille_de_territoire


