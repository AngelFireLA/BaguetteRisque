import pygame
from classes import *
from utils import *
import random
# basic pygame window
pygame.init()
screen = pygame.display.set_mode((819, 819))
pygame.display.set_caption("Baguette Risque")


def load_icons():
    global armée, capitale, exploitation_pétrole, navire, port, port_secondaire, route_payante, soldats_alliés_1, soldats_alliés_2, usine, usine_charbon
    armée = pygame.image.load("images/armée.png").convert_alpha()
    capitale = pygame.image.load("images/capitale.png").convert_alpha()
    exploitation_pétrole = pygame.image.load("images/exploitation_pétrole.png").convert_alpha()
    navire = pygame.image.load("images/navire.png").convert_alpha()
    port = pygame.image.load("images/port.png").convert_alpha()
    port_secondaire = pygame.image.load("images/port_secondaire.png").convert_alpha()
    route_payante = pygame.image.load("images/route_payante.png").convert_alpha()
    soldats_alliés_1 = pygame.image.load("images/soldats_alliés_1.png").convert_alpha()
    soldats_alliés_2 = pygame.image.load("images/soldats_alliés_2.png").convert_alpha()
    usine = pygame.image.load("images/usine.png").convert_alpha()
    usine_charbon = pygame.image.load("images/usine_charbon.png").convert_alpha()


world_map = pygame.image.load("images/map.png").convert_alpha()

world_map = pygame.transform.scale(world_map, (819, 819))

load_icons()

game = Game()
joueur1 = Joueur("Alice", (255, 0, 0))
joueur2 = Joueur("Bob", (0, 0, 255))
game.ajouter_joueur_depuis_classe(joueur1)
game.ajouter_joueur_depuis_classe(joueur2)

game.initialisation()
running = True
state = "menu"
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pass
    if state == "menu":
        #fill screen in light brown
        screen.fill((181, 101, 29))
    if state == "map_visualizing":
        screen.blit(world_map, (0, 0))


    pygame.display.flip()

pygame.quit()
quit()
