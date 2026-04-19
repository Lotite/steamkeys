from src.scraping.spider_utils import *
from src.scraping.scraper_config import ENEBA_CONF , G2A_CONF , ALLKEYSHOP_CONF , DRIFFLE_CONF , GAMESEAL_CONF , GAMIVO_CONF
from src.Models.dtos import GAME_DTO

from src.steam.steamRequest import *


# # spi = spider(ALLKEYSHOP_CONF())
spi = spider(GAMIVO_CONF(),hidden=False)

games = spi.scraping_game("ark")

print(games)

# games = GetGameList(40 * 250)

# for name in games["name"]:
#     scrapin_game_stores(name)
    

# print(games)



# print(GetSteamInfoByName("hollow knight"))
# print(GetSteamInfoById(3240220))
