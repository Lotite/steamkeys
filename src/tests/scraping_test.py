from scraping.spider_utils import *
from scraping.scraper_config import ENEBA_CONF , G2A_CONF , ALLKEYSHOP_CONF , DRIFFLE_CONF , GAMESEAL_CONF , GAMIVO_CONF
from Models.dtos import GAME_DTO

from steam.steamRequest import *


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
