from src.scraping.spider_utils import spider
from src.scraping.scraper_config import ENEBA_CONF , G2A_CONF
from src.Models.dtos import GAME_DTO

spi = spider(G2A_CONF())

dtos:list[GAME_DTO] = spi.scraping_game("Dragon")

print("Final")
print(len(dtos))
for dto in dtos:
    print(dto.to_dict())