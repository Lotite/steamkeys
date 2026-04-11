from src.scraping.spider_utils import *
from src.scraping.scraper_config import ENEBA_CONF , G2A_CONF , ALLKEYSHOP_CONF , DRIFFLE_CONF
from src.Models.dtos import GAME_DTO

from src.steam.steamRequest import *


# # spi = spider(ALLKEYSHOP_CONF())
# spi = spider(DRIFFLE_CONF())

# spi.scraping_game("Dragon")



games = GetGameList(40)

for name in games["name"]:
    scrapin_game_stores(name)
    

# print(games)



# print(GetSteamInfoByName("hollow knight"))
# print(GetSteamInfoById(3240220))
