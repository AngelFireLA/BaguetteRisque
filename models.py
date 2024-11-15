import random
from PIL import Image

class Army:
    def __init__(self, army_id, owner, location, strength=1):
        self.army_id = army_id  # Identifiant unique de l'armée
        self.owner = owner  # Propriétaire de l'armée (Player)
        self.location = location  # Territoire où l'armée est stationnée
        self.strength = strength  # Nombre de soldats dans l'armée
        self.upkeep_cost = 10  # Coût d'entretien de l'armée (-10฿ par tour)
        self.is_moving = False  # Indique si l'armée est en mouvement
        self.has_moved_this_turn = False  # Indique si l'armée a déjà été déplacée ce tour
        self.is_in_combat = False  # Indique si l'armée est engagée dans un combat
        self.penalty = 0  # Pénalité après une défaite (-1 pour chaque défaite)

    def move_to(self, destination):
        """Déplace l'armée vers un territoire adjacent ou à l'intérieur du même pays."""
        if self.has_moved_this_turn:
            print("Cette armée a déjà été déplacée ce tour.")
            return False

        # Vérifier si le déplacement est possible
        if destination in self.location.adjacent_territories or destination.owner == self.owner:
            # Gestion du fleuve
            if self.location.has_river_to(destination):
                self.owner.turns_to_wait += 1  # Prend un tour supplémentaire
            self.location.remove_army(self)
            destination.add_army(self)
            self.location = destination
            self.has_moved_this_turn = True
            return True
        else:
            print("Déplacement impossible vers ce territoire.")
            return False

    def engage_in_combat(self, enemy_army):
        """Engage un combat avec une armée ennemie."""
        self.is_in_combat = True
        enemy_army.is_in_combat = True

        # Calcul des forces
        attacker_strength = self.calculate_combat_strength(is_attacking=True)
        defender_strength = enemy_army.calculate_combat_strength(is_attacking=False)

        # Calcul du ratio pour la roue
        total_strength = attacker_strength + defender_strength
        attacker_ratio = attacker_strength / total_strength
        defender_ratio = defender_strength / total_strength

        # Simulation de la roue
        outcome = random.choices(
            ['attacker_win', 'defender_win'],
            weights=[attacker_ratio, defender_ratio],
            k=1
        )[0]

        # Application du résultat
        if outcome == 'attacker_win':
            enemy_army.apply_battle_outcome('defeat')
            self.apply_battle_outcome('victory')
        else:
            self.apply_battle_outcome('defeat')
            enemy_army.apply_battle_outcome('victory')

    def calculate_combat_strength(self, is_attacking):
        """Calcule la force de combat de l'armée pour le calcul de la bataille."""
        if is_attacking:
            # Pour l'attaquant : +3 par soldat
            strength = self.strength * 3
        else:
            # Pour le défenseur : +1 par soldat
            strength = self.strength * 1
            # Bonus si usine, port ou capitale
            if self.location.has_special_infrastructure():
                strength += 1
            # Bonus de terrain
            if self.location.is_mountainous():
                strength += 2
            # Taille du territoire
            territory_size_bonus = max(1, self.location.size // 5000)
            strength += territory_size_bonus
            # Navires proches
            nearby_ships = self.location.count_nearby_ships(self.owner)
            strength += nearby_ships
        # Appliquer les pénalités éventuelles
        strength += self.penalty
        return strength

    def apply_battle_outcome(self, result):
        """Applique le résultat d'une bataille à l'armée."""
        if result == 'victory':
            print(f"L'armée {self.army_id} a remporté la bataille.")
            # Réinitialiser la pénalité
            self.penalty = 0
            # Réinitialiser la pénalité de production du joueur si applicable
            self.owner.reset_production_penalty()
        elif result == 'defeat':
            print(f"L'armée {self.army_id} a perdu la bataille.")
            # Perte de 1/3 des soldats
            losses = max(1, self.strength // 3)
            self.strength -= losses
            # Vérifier si l'armée est détruite
            if self.strength <= 0:
                self.disband()
            else:
                # Reculer l'armée
                self.retreat()
                # Appliquer la pénalité
                self.penalty -= 1
                # Ralentissement de la production du joueur
                self.owner.apply_production_penalty()

    def retreat(self):
        """Fait reculer l'armée vers un territoire ami."""
        # Trouver un territoire ami adjacent
        for territory in self.location.adjacent_territories:
            if territory.owner == self.owner:
                self.location.remove_army(self)
                territory.add_army(self)
                self.location = territory
                print(f"L'armée {self.army_id} a reculé vers {territory.name}.")
                return
        # Si aucun territoire ami, l'armée est détruite
        print(f"L'armée {self.army_id} n'a pas pu reculer et est détruite.")
        self.disband()

    def disband(self):
        """Dissout l'armée."""
        self.location.remove_army(self)
        self.owner.armies.remove(self)
        print(f"L'armée {self.army_id} a été dissoute.")

    def reset_for_new_turn(self):
        """Réinitialise les états pour le nouveau tour."""
        self.has_moved_this_turn = False
        self.is_in_combat = False
        self.is_moving = False


class Fleet:
    def __init__(self, fleet_id, owner, location, ships=1):
        self.fleet_id = fleet_id  # Identifiant unique de la flotte
        self.owner = owner  # Propriétaire de la flotte (Player)
        self.location = location  # Zone maritime où la flotte est stationnée
        self.ships = ships  # Nombre de navires dans la flotte
        self.upkeep_cost = 20  # Coût d'entretien de la flotte (-20฿ par tour)
        self.is_moving = False  # Indique si la flotte est en mouvement
        self.has_moved_this_turn = False  # Indique si la flotte a déjà été déplacée ce tour
        self.armies_transported = []  # Armées transportées par la flotte
        self.is_in_combat = False  # Indique si la flotte est engagée dans un combat naval

    def move_to(self, destination):
        """Déplace la flotte vers une autre zone maritime."""
        if self.has_moved_this_turn:
            print("Cette flotte a déjà été déplacée ce tour.")
            return False

        # Vérifier le nombre de cases à parcourir
        distance = self.location.calculate_distance(destination)
        turns_needed = (distance // 2) or 1  # Chaque 2 cases prend 1 tour

        self.owner.turns_to_wait += turns_needed - 1  # Ajuster le temps d'attente si nécessaire
        self.location.remove_fleet(self)
        destination.add_fleet(self)
        self.location = destination
        self.has_moved_this_turn = True
        return True

    def engage_in_naval_combat(self, enemy_fleet):
        """Engage un combat naval avec une flotte ennemie."""
        self.is_in_combat = True
        enemy_fleet.is_in_combat = True

        # Calcul des forces
        attacker_strength = self.calculate_combat_strength()
        defender_strength = enemy_fleet.calculate_combat_strength()

        # Calcul du ratio pour la roue
        total_strength = attacker_strength + defender_strength
        attacker_ratio = attacker_strength / total_strength
        defender_ratio = defender_strength / total_strength

        # Simulation de la roue
        outcome = random.choices(
            ['attacker_win', 'defender_win'],
            weights=[attacker_ratio, defender_ratio],
            k=1
        )[0]

        # Application du résultat
        if outcome == 'attacker_win':
            enemy_fleet.apply_battle_outcome('defeat')
            self.apply_battle_outcome('victory')
        else:
            self.apply_battle_outcome('defeat')
            enemy_fleet.apply_battle_outcome('victory')

    def calculate_combat_strength(self):
        """Calcule la force de combat de la flotte pour le calcul de la bataille navale."""
        # +1 par navire
        strength = self.ships * 1
        # +2 par exploitation de pétrole dans la case
        oil_exploitations = self.location.count_infrastructure('Oil Exploitation', self.owner)
        strength += oil_exploitations * 2
        # +1 par soldat transporté
        total_soldiers = sum(army.strength for army in self.armies_transported)
        strength += total_soldiers * 1
        return strength

    def apply_battle_outcome(self, result):
        """Applique le résultat d'une bataille navale à la flotte."""
        if result == 'victory':
            print(f"La flotte {self.fleet_id} a remporté la bataille navale.")
            # Bonus pour la prochaine bataille terrestre
            self.owner.naval_victories += 1
        elif result == 'defeat':
            print(f"La flotte {self.fleet_id} a perdu la bataille navale.")
            # Perte de navires
            losses = max(1, self.ships // 3)
            self.ships -= losses
            # Vérifier si la flotte est détruite
            if self.ships <= 0:
                self.disband()
            else:
                # Reculer la flotte
                self.retreat()

    def transport_armies(self, armies):
        """Charge des armées à bord de la flotte."""
        if len(armies) + len(self.armies_transported) <= self.ships * 2:
            self.armies_transported.extend(armies)
            for army in armies:
                army.location = self.location
            print(f"Armées transportées par la flotte {self.fleet_id}.")
        else:
            print("Pas assez de capacité pour transporter toutes les armées.")

    def unload_armies(self, destination):
        """Décharge les armées transportées sur un territoire."""
        for army in self.armies_transported:
            destination.add_army(army)
            army.location = destination
        self.armies_transported.clear()
        print(f"Armées déchargées sur {destination.name}.")

    def retreat(self):
        """Fait reculer la flotte vers une zone maritime amie."""
        # Trouver une zone maritime amie adjacente
        for sea_zone in self.location.adjacent_sea_zones:
            if sea_zone.is_controlled_by(self.owner):
                self.location.remove_fleet(self)
                sea_zone.add_fleet(self)
                self.location = sea_zone
                print(f"La flotte {self.fleet_id} a reculé vers {sea_zone.name}.")
                return
        # Si aucune zone amie, la flotte est détruite
        print(f"La flotte {self.fleet_id} n'a pas pu reculer et est détruite.")
        self.disband()

    def disband(self):
        """Dissout la flotte."""
        self.owner.fleets.remove(self)
        print(f"La flotte {self.fleet_id} a été dissoute.")

    def reset_for_new_turn(self):
        """Réinitialise les états pour le nouveau tour."""
        self.has_moved_this_turn = False
        self.is_in_combat = False
        self.is_moving = False


class Player:
    def __init__(self, player_id, name, color, flag_image_path):
        self.player_id = player_id  # Identifiant unique du joueur
        self.name = name  # Nom du joueur
        self.color = color  # Couleur associée au joueur
        self.flag = Image.open(flag_image_path)
        self.territories = []  # Liste des territoires contrôlés par le joueur
        self.armies = []  # Liste des armées appartenant au joueur
        self.fleets = []  # Liste des flottes appartenant au joueur
        self.allies = []  # Liste des alliés du joueur
        self.war_declarations = []  # Liste des pays en guerre
        self.puppet_states = []  # États fantoches contrôlés
        self.ideology = None  # Idéologie du joueur
        self.action_points = {'military': 2, 'diplomatic': 2, 'bonus': 1}  # Points d'action disponibles
        self.turns_to_wait = 0  # Tours à attendre en cas de pénalité
        self.naval_victories = 0  # Nombre de victoires navales
        self.production_penalty = False  # Indique si la production est ralentie
        self.current_turn = 1  # Compteur de tours

        # Ressources initiales
        self.resources = {
            'money': random.choice([1000, 5000, 10000, 25000, 50000]),
            'population': random.choice([20, 50, 100, 500]),
        }

        # Générer le territoire initial
        self.initial_territory_size = random.randint(1000, 25000)
        self.generate_initial_territory()

        # Générer les armées et flottes initiales
        self.initialize_military_units()

        # Dépense militaire initiale
        self.military_spending_level = 1  # Niveau de dépense militaire (1, 2 ou 4)
        self.soldier_production = 0  # Nombre de soldats produits par tour

    def generate_initial_territory(self):
        """Génère le territoire initial du joueur."""
        capital = Territory(
            territory_id=f"{self.player_id}_capital",
            name=f"Capitale de {self.name}",
            size=self.initial_territory_size,
            owner=self,
            resources={'wealth': 0, 'population': self.resources['population']},
            terrain_type='plains',
            is_capital=True,
            is_port=False,
            relief_level=random.randint(1, 7),
            depth_level=random.randint(1, 7)
        )
        self.territories.append(capital)

    def initialize_military_units(self):
        """Initialise les armées et flottes du joueur."""
        initial_armies = random.randint(1, 5)
        for _ in range(initial_armies):
            army = Army(
                army_id=f"{self.player_id}_army_{len(self.armies)}",
                owner=self,
                location=self.territories[0],
                strength=1
            )
            self.armies.append(army)
            self.territories[0].add_army(army)

        # Vérifier si le joueur a un accès maritime
        if self.has_coastal_territory():
            initial_fleets = random.randint(1, 5)
            for _ in range(initial_fleets):
                fleet = Fleet(
                    fleet_id=f"{self.player_id}_fleet_{len(self.fleets)}",
                    owner=self,
                    location=self.get_coastal_territory(),
                    ships=1
                )
                self.fleets.append(fleet)
                self.get_coastal_territory().add_fleet(fleet)

    def has_coastal_territory(self):
        """Vérifie si le joueur possède un territoire côtier."""
        for territory in self.territories:
            if territory.is_coastal:
                return True
        return False

    def get_coastal_territory(self):
        """Retourne un territoire côtier du joueur."""
        for territory in self.territories:
            if territory.is_coastal:
                return territory
        return None

    def update_resources(self):
        """Met à jour les ressources du joueur en appliquant les revenus et les dépenses."""
        income = self.calculate_income()
        expenses = self.calculate_expenses()
        self.resources['money'] += income - expenses

    def calculate_income(self):
        """Calcule les revenus totaux du joueur pour le tour."""
        income = 0
        for territory in self.territories:
            income += territory.calculate_production()
        # Appliquer la pénalité de production si nécessaire
        if self.production_penalty:
            income /= 2  # Divise les revenus par 2
        return income

    def calculate_expenses(self):
        """Calcule les dépenses totales du joueur pour le tour."""
        expenses = 0
        # Coûts d'entretien des armées
        for army in self.armies:
            expenses += army.upkeep_cost
        # Coûts d'entretien des flottes
        for fleet in self.fleets:
            expenses += fleet.upkeep_cost
        # Coûts d'entretien des infrastructures
        for territory in self.territories:
            for infrastructure in territory.infrastructures:
                expenses += infrastructure.upkeep_cost
        return expenses

    def produce_soldiers(self):
        """Produit des soldats en fonction du niveau de dépense militaire."""
        production_rates = {1: 1, 2: 2, 4: 4}
        self.soldier_production = production_rates.get(self.military_spending_level, 1)
        for _ in range(self.soldier_production):
            army = Army(
                army_id=f"{self.player_id}_army_{len(self.armies)}",
                owner=self,
                location=self.get_capital(),
                strength=1
            )
            self.armies.append(army)
            self.get_capital().add_army(army)

    def change_military_spending(self, new_level):
        """Change le niveau de dépense militaire."""
        if self.action_points['military'] > 0 and new_level in [1, 2, 4]:
            self.military_spending_level = new_level
            self.action_points['military'] -= 1
            print(f"{self.name} a changé son niveau de dépense militaire à {new_level}.")
        else:
            print("Impossible de changer le niveau de dépense militaire.")

    def get_capital(self):
        """Retourne le territoire qui est la capitale."""
        for territory in self.territories:
            if territory.is_capital:
                return territory
        return None

    def apply_production_penalty(self):
        """Applique une pénalité de production après une défaite."""
        self.production_penalty = True

    def reset_production_penalty(self):
        """Réinitialise la pénalité de production après une victoire."""
        self.production_penalty = False

    def update_action_points(self):
        """Recharge les points d'action pour le nouveau tour."""
        self.action_points = {'military': 2, 'diplomatic': 2, 'bonus': 1}

    def next_turn(self):
        """Prépare le joueur pour le prochain tour."""
        self.current_turn += 1
        self.update_action_points()
        self.update_resources()
        self.produce_soldiers()
        for army in self.armies:
            army.reset_for_new_turn()
        for fleet in self.fleets:
            fleet.reset_for_new_turn()
        # Réinitialiser la pénalité de production si nécessaire
        if self.production_penalty and not self.has_recent_defeats():
            self.reset_production_penalty()

    def has_recent_defeats(self):
        """Vérifie si le joueur a eu des défaites récentes."""
        # Pour simplifier, on considère que la pénalité s'applique pour un tour après la défaite
        # Vous pouvez ajuster cette logique selon les règles exactes de votre jeu
        return self.production_penalty

    def declare_war(self, enemy_player):
        """Déclare la guerre à un autre joueur."""
        if self.action_points['diplomatic'] >= 2:
            self.war_declarations.append(enemy_player)
            self.action_points['diplomatic'] -= 2
            print(f"{self.name} a déclaré la guerre à {enemy_player.name}.")
        else:
            print("Pas assez de points d'action diplomatiques pour déclarer la guerre.")

    def manage_alliances(self, other_player, action):
        """Gère les alliances avec d'autres joueurs."""
        if action == 'ally' and self.action_points['diplomatic'] > 0:
            self.allies.append(other_player)
            self.action_points['diplomatic'] -= 1
            print(f"{self.name} s'est allié avec {other_player.name}.")
        elif action == 'break' and other_player in self.allies:
            self.allies.remove(other_player)
            self.action_points['diplomatic'] -= 1
            print(f"{self.name} a rompu son alliance avec {other_player.name}.")
        else:
            print("Action impossible.")

    def change_ideology(self, new_ideology):
        """Change l'idéologie du joueur."""
        if self.action_points['diplomatic'] > 0:
            self.ideology = new_ideology
            self.apply_ideology_effects()
            self.action_points['diplomatic'] -= 1
            print(f"{self.name} a adopté l'idéologie {new_ideology}.")
        else:
            print("Pas assez de points d'action diplomatiques pour changer d'idéologie.")

    def apply_ideology_effects(self):
        """Applique les effets de l'idéologie choisie."""
        # Réinitialiser les modifications précédentes
        self.reset_ideology_effects()
        if self.ideology == 'République':
            # Enlève l'effet de désavantage après 2 défaites
            pass  # Implémentation selon les règles du jeu
        elif self.ideology == 'Royauté':
            # Bonus de +1 par ratio de conquête
            pass
        elif self.ideology == 'Empire':
            # Bonus de +2 par ratio de conquête
            pass
        elif self.ideology == 'Socialisme':
            # Diminue la production d'argent par -10%
            # Augmente la production des soldats par +1
            # Diminue le coût d’entretien de chaque armée/navire
            self.apply_socialism_effects()
        elif self.ideology == 'Dictature':
            # Augmente la production de soldats par +2
            self.soldier_production += 2

    def reset_ideology_effects(self):
        """Réinitialise les effets de l'idéologie."""
        # Remettre les coûts d'entretien à leurs valeurs par défaut
        for army in self.armies:
            army.upkeep_cost = 10
        for fleet in self.fleets:
            fleet.upkeep_cost = 20

    def apply_socialism_effects(self):
        """Applique les effets spécifiques du socialisme."""
        # Diminue la production d'argent par -10%
        # Note : Cela pourrait être appliqué dans calculate_income avec un check sur l'idéologie
        self.resources['money'] *= 0.9
        # Augmente la production des soldats par +1
        self.soldier_production += 1
        # Diminue le coût d’entretien de chaque armée/navire
        for army in self.armies:
            army.upkeep_cost = 5
        for fleet in self.fleets:
            fleet.upkeep_cost = 10

    def build_infrastructure(self, territory, infrastructure_type):
        """Construit une nouvelle infrastructure sur un territoire spécifié."""
        if self.action_points['bonus'] > 0 and territory.can_build_infrastructure(infrastructure_type):
            cost = random.randint(5000, 7500)
            if self.resources['money'] >= cost:
                infrastructure = Infrastructure(
                    infrastructure_id=f"{territory.territory_id}_{infrastructure_type}_{len(territory.infrastructures)}",
                    name=f"{infrastructure_type} sur {territory.name}",
                    infrastructure_type=infrastructure_type,
                    owner=self,
                    location=territory
                )
                territory.add_infrastructure(infrastructure)
                self.resources['money'] -= cost
                self.action_points['bonus'] -= 1
                print(f"{self.name} a construit {infrastructure_type} sur {territory.name}.")
            else:
                print("Pas assez d'argent pour construire cette infrastructure.")
        else:
            print("Impossible de construire cette infrastructure.")

    def move_unit(self, unit, destination):
        """Déplace une unité vers une destination spécifiée."""
        if isinstance(unit, Army) or isinstance(unit, Fleet):
            if self.action_points['military'] > 0:
                moved = unit.move_to(destination)
                if moved:
                    self.action_points['military'] -= 1
                else:
                    print("L'unité n'a pas pu se déplacer.")
            else:
                print("Pas assez de points d'action militaires pour déplacer l'unité.")
        else:
            print("Type d'unité invalide.")

    def colonize(self, sea_zone):
        """Colonise un nouveau territoire via une flotte."""
        if self.action_points['bonus'] > 0:
            # Déplacer une flotte à l'endroit voulu
            fleet = self.select_available_fleet()
            if fleet:
                moved = fleet.move_to(sea_zone)
                if moved:
                    # Lancer la roue pour déterminer la taille du territoire
                    territory_size = random.randint(5000, 50000)
                    new_territory = Territory(
                        territory_id=f"{self.player_id}_colony_{len(self.territories)}",
                        name=f"Colonie de {self.name}",
                        size=territory_size,
                        owner=self,
                        resources={'wealth': 0, 'population': 0},
                        terrain_type='plains',
                        is_capital=False,
                        is_port=True
                    )
                    self.territories.append(new_territory)
                    # Ajouter un port, une usine simple et 2 soldats
                    port = Infrastructure(
                        infrastructure_id=f"{new_territory.territory_id}_port",
                        name=f"Port de {new_territory.name}",
                        infrastructure_type='Port',
                        owner=self,
                        location=new_territory
                    )
                    new_territory.add_infrastructure(port)
                    for _ in range(2):
                        army = Army(
                            army_id=f"{self.player_id}_army_{len(self.armies)}",
                            owner=self,
                            location=new_territory,
                            strength=1
                        )
                        self.armies.append(army)
                        new_territory.add_army(army)
                    self.action_points['bonus'] -= 1
                    print(f"{self.name} a colonisé un nouveau territoire : {new_territory.name}.")
                else:
                    print("La flotte n'a pas pu se déplacer pour coloniser.")
            else:
                print("Aucune flotte disponible pour la colonisation.")
        else:
            print("Pas assez de points d'action bonus pour coloniser.")

    def select_available_fleet(self):
        """Sélectionne une flotte disponible pour la colonisation."""
        for fleet in self.fleets:
            if not fleet.has_moved_this_turn:
                return fleet
        return None

    def get_total_territory_size(self):
        """Calcule la taille totale du territoire du joueur."""
        return sum(territory.size for territory in self.territories)

# Les autres classes (Territory, Infrastructure, SeaZone, Map, Game) doivent être également revues de la même manière.
# Voici les classes mises à jour pour éviter les problèmes de méthodes ou attributs manquants.

class Territory:
    def __init__(self, territory_id, name, size, owner, resources, terrain_type, is_capital=False, is_port=False, relief_level=1, depth_level=1):
        self.territory_id = territory_id  # Identifiant unique du territoire
        self.name = name  # Nom du territoire
        self.size = size  # Taille en pixels du territoire
        self.owner = owner  # Propriétaire actuel (Player)
        self.resources = {
            'wealth': resources.get('wealth', 0),  # Richesse générée par le territoire
            'population': resources.get('population', 0)  # Population du territoire
        }
        self.armies = []  # Armées stationnées sur le territoire
        self.fleets = []  # Flottes stationnées dans les eaux adjacentes
        self.terrain_type = terrain_type  # Type de terrain (plaine, montagne, etc.)
        self.infrastructures = []  # Liste des infrastructures (usines, ports, etc.)
        self.is_capital = is_capital  # Indique si le territoire est la capitale du joueur
        self.is_port = is_port  # Indique si le territoire possède un port
        self.is_coastal = is_port  # Indique si le territoire est côtier
        self.relief_level = relief_level  # Niveau de relief (pour les usines à charbon)
        self.depth_level = depth_level  # Niveau de profondeur (pour les exploitations pétrolières)
        self.adjacent_territories = []  # Territoires adjacents
        self.adjacent_sea_zones = []  # Zones maritimes adjacentes
        self.strategic_value = 0  # Valeur stratégique influençant les combats et la production

    def change_owner(self, new_owner):
        """Change le propriétaire du territoire."""
        self.owner = new_owner

    def add_army(self, army):
        """Ajoute une armée sur le territoire."""
        self.armies.append(army)
        army.location = self

    def remove_army(self, army):
        """Retire une armée du territoire."""
        if army in self.armies:
            self.armies.remove(army)
            army.location = None

    def add_fleet(self, fleet):
        """Ajoute une flotte dans la zone maritime adjacente."""
        self.fleets.append(fleet)
        fleet.location = self

    def remove_fleet(self, fleet):
        """Retire une flotte de la zone maritime adjacente."""
        if fleet in self.fleets:
            self.fleets.remove(fleet)
            fleet.location = None

    def add_infrastructure(self, infrastructure):
        """Ajoute une infrastructure (usine, port) au territoire."""
        self.infrastructures.append(infrastructure)
        if infrastructure.infrastructure_type == 'Port':
            self.is_port = True
            self.is_coastal = True

    def calculate_production(self):
        """Calcule la production économique du territoire."""
        production = self.resources['wealth']
        for infrastructure in self.infrastructures:
            production += infrastructure.calculate_production()
        return production

    def can_build_infrastructure(self, infrastructure_type):
        """Vérifie si une infrastructure peut être construite sur ce territoire."""
        if infrastructure_type == 'Oil Exploitation' and self.depth_level in range(5, 8):
            return True
        if infrastructure_type == 'Coal Factory' and self.relief_level in range(4, 7):
            return True
        if infrastructure_type in ['Factory', 'Port', 'Additional Port']:
            return True
        return False

    def has_special_infrastructure(self):
        """Vérifie si le territoire possède une usine, un port ou est la capitale."""
        return self.is_capital or any(
            infra.infrastructure_type in ['Factory', 'Port'] for infra in self.infrastructures
        )

    def is_mountainous(self):
        """Vérifie si le territoire est montagneux."""
        return self.terrain_type == 'mountain'

    def has_river_to(self, destination):
        """Vérifie si un fleuve se dresse entre ce territoire et la destination."""
        # Implémentation simplifiée pour l'exemple
        # Vous pouvez ajouter une logique réelle en fonction de votre carte
        return False  # Supposons qu'il n'y a pas de fleuve par défaut

    def count_nearby_ships(self, player):
        """Compte le nombre de navires proches appartenant au joueur."""
        count = 0
        for sea_zone in self.adjacent_sea_zones:
            for fleet in sea_zone.fleets:
                if fleet.owner == player:
                    count += fleet.ships
        return count

class Infrastructure:
    def __init__(self, infrastructure_id, name, infrastructure_type, owner, location):
        self.infrastructure_id = infrastructure_id  # Identifiant unique de l'infrastructure
        self.name = name  # Nom de l'infrastructure
        self.infrastructure_type = infrastructure_type  # Type (usine, port, etc.)
        self.owner = owner  # Propriétaire (Player)
        self.location = location  # Territoire
        self.production_bonus = 0  # Bonus de production
        self.upkeep_cost = 0  # Coût d'entretien
        self.is_active = True  # Statut de l'infrastructure
        self.level = 1  # Niveau de l'infrastructure
        self.capacity = 100  # Capacité maximale
        self.set_default_values()

    def set_default_values(self):
        """Définit les valeurs par défaut en fonction du type d'infrastructure."""
        if self.infrastructure_type == 'Factory':
            self.production_bonus = 15
            self.upkeep_cost = 5
        elif self.infrastructure_type == 'Port':
            self.production_bonus = 100
            self.upkeep_cost = 10
        elif self.infrastructure_type == 'Additional Port':
            self.production_bonus = 50
            self.upkeep_cost = 5
        elif self.infrastructure_type == 'Oil Exploitation':
            self.production_bonus = 150
            self.upkeep_cost = 20
        elif self.infrastructure_type == 'Coal Factory':
            self.production_bonus = 50
            self.upkeep_cost = 10

    def calculate_production(self):
        """Calcule la production générée."""
        if self.is_active:
            if self.infrastructure_type in ['Oil Exploitation', 'Coal Factory']:
                if self.owner.current_turn % 2 == 0:
                    return self.production_bonus * self.level
                else:
                    return 0
            else:
                return self.production_bonus * self.level
        return 0

    def can_support(self, unit_type):
        """Vérifie si l'infrastructure peut soutenir une unité."""
        if self.infrastructure_type == 'Port' and unit_type == 'Fleet':
            return True
        if self.infrastructure_type == 'Factory' and unit_type == 'Army':
            return True
        return False

class SeaZone:
    def __init__(self, sea_zone_id, name):
        self.sea_zone_id = sea_zone_id  # Identifiant unique de la zone maritime
        self.name = name  # Nom de la zone maritime
        self.adjacent_sea_zones = []  # Zones maritimes adjacentes
        self.adjacent_territories = []  # Territoires adjacents
        self.fleets = []  # Flottes présentes dans la zone
        self.controlled_by = None  # Joueur contrôlant la zone (si applicable)

    def add_fleet(self, fleet):
        """Ajoute une flotte dans la zone maritime."""
        self.fleets.append(fleet)
        fleet.location = self

    def remove_fleet(self, fleet):
        """Retire une flotte de la zone maritime."""
        if fleet in self.fleets:
            self.fleets.remove(fleet)
            fleet.location = None

    def is_controlled_by(self, player):
        """Vérifie si la zone maritime est contrôlée par un joueur."""
        # Simplification : Une zone est contrôlée si un joueur a une flotte dans cette zone
        for fleet in self.fleets:
            if fleet.owner == player:
                return True
        return False

    def calculate_distance(self, destination):
        """Calcule la distance en nombre de cases vers une autre zone maritime."""
        # Implémentation simplifiée pour l'exemple
        # Vous pouvez utiliser un algorithme de graphe pour calculer la distance réelle
        return 1  # Supposons une distance de 1 par défaut

    def count_infrastructure(self, infrastructure_type, owner):
        """Compte le nombre d'infrastructures spécifiques dans les territoires adjacents."""
        count = 0
        for territory in self.adjacent_territories:
            for infra in territory.infrastructures:
                if infra.infrastructure_type == infrastructure_type and infra.owner == owner:
                    count += 1
        return count

class Map:
    def __init__(self):
        self.territories = []  # Liste des territoires sur la carte
        self.sea_zones = []  # Liste des zones maritimes sur la carte

    def generate_territories(self):
        """Génère les territoires de la carte."""
        # Implémentation pour créer les territoires
        # Par exemple, créer un certain nombre de territoires aléatoirement
        for i in range(50):  # Nombre de territoires à générer
            territory = Territory(
                territory_id=f"territory_{i}",
                name=f"Territoire {i}",
                size=random.randint(1000, 25000),
                owner=None,
                resources={'wealth': random.randint(1000, 5000), 'population': random.randint(20, 500)},
                terrain_type=random.choice(['plains', 'mountain']),
                relief_level=random.randint(1, 7),
                depth_level=random.randint(1, 7)
            )
            self.territories.append(territory)
        # Définir les territoires adjacents
        self.set_adjacent_territories()

    def generate_sea_zones(self):
        """Génère les zones maritimes de la carte."""
        for i in range(20):  # Nombre de zones maritimes à générer
            sea_zone = SeaZone(
                sea_zone_id=f"sea_zone_{i}",
                name=f"Zone Maritime {i}"
            )
            self.sea_zones.append(sea_zone)
        # Définir les zones maritimes adjacentes
        self.set_adjacent_sea_zones()

    def set_adjacent_territories(self):
        """Définit les territoires adjacents pour chaque territoire."""
        for i, territory in enumerate(self.territories):
            adjacent_indices = [i - 1, i + 1]
            for idx in adjacent_indices:
                if 0 <= idx < len(self.territories):
                    territory.adjacent_territories.append(self.territories[idx])

    def set_adjacent_sea_zones(self):
        """Définit les zones maritimes adjacentes pour chaque zone maritime."""
        for i, sea_zone in enumerate(self.sea_zones):
            adjacent_indices = [i - 1, i + 1]
            for idx in adjacent_indices:
                if 0 <= idx < len(self.sea_zones):
                    sea_zone.adjacent_sea_zones.append(self.sea_zones[idx])

    def get_adjacent_territories(self, territory):
        """Retourne les territoires adjacents à un territoire donné."""
        return territory.adjacent_territories

    def get_adjacent_sea_zones(self, sea_zone):
        """Retourne les zones maritimes adjacentes à une zone donnée."""
        return sea_zone.adjacent_sea_zones

class Game:
    def __init__(self):
        self.players = []  # Liste des joueurs participant à la partie
        self.current_turn = 1  # Numéro du tour actuel
        self.max_turns = 10000  # Nombre maximal de tours (peut être ajusté)
        self.map = None  # Carte du jeu (instance de la classe Map)
        self.active_player_index = 0  # Indice du joueur dont c'est le tour
        self.is_game_over = False  # Indique si la partie est terminée
        self.victory_conditions = {
            'largest_army': None,
            'largest_navy': None,
            'largest_territory': None,
            'richest': None
        }
        self.game_log = []  # Historique des actions et événements du jeu

        # Initialiser la carte du jeu
        self.initialize_map()

    def initialize_map(self):
        """Initialise la carte du jeu avec les territoires et les zones maritimes."""
        self.map = Map()
        self.map.generate_territories()
        self.map.generate_sea_zones()

    def add_player(self, name, color, flag_image_path):
        """Ajoute un joueur à la partie."""
        player_id = f"player_{len(self.players) + 1}"
        new_player = Player(player_id, name, color, flag_image_path)
        self.players.append(new_player)
        print(f"Joueur {name} ajouté à la partie.")

    def setup_game(self):
        """Prépare le jeu avant le début de la partie."""
        # Assigner les territoires initiaux aux joueurs
        self.assign_initial_territories()
        # Définir l'ordre de jeu (peut être aléatoire)
        random.shuffle(self.players)
        print("Le jeu est prêt à commencer.")

    def assign_initial_territories(self):
        """Assigne des territoires initiaux à chaque joueur."""
        for player in self.players:
            # Sélectionner un territoire non assigné aléatoirement
            available_territories = [t for t in self.map.territories if t.owner is None]
            if available_territories:
                initial_territory = random.choice(available_territories)
                initial_territory.change_owner(player)
                player.territories.append(initial_territory)
                print(f"{player.name} a reçu le territoire {initial_territory.name} comme capitale.")
            else:
                print("Plus de territoires disponibles pour l'assignation initiale.")

    def start_game(self):
        """Démarre la partie."""
        self.is_game_over = False
        print("La partie commence !")
        while not self.is_game_over and self.current_turn <= self.max_turns:
            print(f"\n--- Tour {self.current_turn} ---")
            for player in self.players:
                self.active_player_index = self.players.index(player)
                self.process_player_turn(player)
                if self.check_victory_conditions(player):
                    self.is_game_over = True
                    break
            self.current_turn += 1
        self.end_game()

    def process_player_turn(self, player):
        """Gère le tour d'un joueur."""
        print(f"\nC'est le tour de {player.name}.")
        player.next_turn()

        # Ici, vous pouvez implémenter la logique pour permettre au joueur de prendre des actions
        # Par exemple, demander à l'utilisateur de choisir ses actions
        # Pour ce contexte, nous allons simuler des actions aléatoires
        self.simulate_player_actions(player)

    def simulate_player_actions(self, player):
        """Simule des actions pour le joueur (à remplacer par une interface utilisateur réelle)."""
        # Exemple d'actions aléatoires
        actions = ['move_unit', 'build_infrastructure', 'declare_war', 'change_ideology']
        for _ in range(player.action_points['military']):
            action = random.choice(actions)
            if action == 'move_unit':
                # Sélectionner une unité et une destination aléatoirement
                if player.armies:
                    army = random.choice(player.armies)
                    available_territories = self.map.get_adjacent_territories(army.location)
                    if available_territories:
                        destination = random.choice(available_territories)
                        player.move_unit(army, destination)
            elif action == 'build_infrastructure':
                # Construire une infrastructure sur un territoire aléatoire
                territory = random.choice(player.territories)
                infra_type = random.choice(['Factory', 'Port', 'Oil Exploitation', 'Coal Factory'])
                player.build_infrastructure(territory, infra_type)
            elif action == 'declare_war':
                # Déclarer la guerre à un autre joueur
                potential_enemies = [p for p in self.players if p != player and p not in player.war_declarations]
                if potential_enemies:
                    enemy = random.choice(potential_enemies)
                    player.declare_war(enemy)
            elif action == 'change_ideology':
                # Changer d'idéologie
                ideologies = ['République', 'Royauté', 'Empire', 'Socialisme', 'Dictature']
                new_ideology = random.choice(ideologies)
                player.change_ideology(new_ideology)

    def check_victory_conditions(self, player):
        """Vérifie si un joueur a rempli une condition de victoire."""
        # Conditions de victoire
        largest_army = max(self.players, key=lambda p: len(p.armies))
        largest_navy = max(self.players, key=lambda p: len(p.fleets))
        largest_territory = max(self.players, key=lambda p: p.get_total_territory_size())
        richest = max(self.players, key=lambda p: p.resources['money'])

        if player == largest_army and player == largest_navy and player == largest_territory and player == richest:
            print(f"\n{player.name} a rempli toutes les conditions de victoire !")
            return True
        return False

    def end_game(self):
        """Termine la partie et affiche les résultats."""
        print("\nLa partie est terminée.")
        # Déterminer le vainqueur selon les conditions de victoire
        winner = max(self.players, key=lambda p: (
            len(p.armies),
            len(p.fleets),
            p.get_total_territory_size(),
            p.resources['money']
        ))
        print(f"Le gagnant est {winner.name} !")
        print("Merci d'avoir joué à Baguette Risque.")

    def save_game_state(self):
        """Sauvegarde l'état actuel du jeu (fonctionnalité optionnelle)."""
        # Implémentation pour sauvegarder l'état du jeu
        pass

    def load_game_state(self):
        """Charge un état de jeu précédemment sauvegardé (fonctionnalité optionnelle)."""
        # Implémentation pour charger un état du jeu
        pass
