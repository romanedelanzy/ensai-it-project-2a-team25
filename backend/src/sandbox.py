from service.game_service import GameService
from business_object.game import Game
from business_object.player import Player
from dao.game_dao import GameDao
from utils.env_variables import display_values, load_environment_variables
from utils.log_utils import initialize_logs

# Initialization
initialize_logs("Webservice")

load_environment_variables()
display_values()

g = GameService().play(3, 5, "coinflip", choice="tails")
g2 = GameService().play(3, 5, "dice")

g.id_game = 44

id = GameDao().create(g)
game2 = GameDao().find_by_id(g.id_game)

result = GameDao().find_all_by_player(4)
print(result[1])
