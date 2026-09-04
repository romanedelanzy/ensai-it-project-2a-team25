from datetime import datetime

from business_object.game import Game
from business_object.player import Player


p1 = Player("use1", 0.5, "exemple@gmail.com")
p2 = Player("use2", 0.3, "2@gmail.com")
g = Game(p1, p2, "Coin flip", p1, "Jeu de lancer de piece", datetime.now())
print(g)