import models
from models import *

# Créer une instance du jeu
game = Game()

# Ajouter des joueurs
game.add_player(name="Alice", color="Red", flag_image_path="images/icone.png")
game.add_player(name="Bob", color="Blue", flag_image_path="images/icone.png")
game.add_player(name="Charlie", color="Green", flag_image_path="images/icone.png")

# Préparer le jeu
game.setup_game()

# Démarrer la partie
game.start_game()
