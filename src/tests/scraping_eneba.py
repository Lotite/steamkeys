from src.scraping.spider_utils import spider
from src.scraping.scraper_config import ENEBA_CONF
from src.Models.dtos import GAME_DTO

spi = spider(ENEBA_CONF())

dtos:list[GAME_DTO] = spi.scraping_game("Dragon")


for dto in dtos:
    print(dto.to_dict())