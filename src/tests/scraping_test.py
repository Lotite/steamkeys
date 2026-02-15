from src.scraping.spider_utils import spider
from src.scraping.scraper_config import ENEBA_CONF , G2A_CONF , ALLKEYSHOP_CONF
from src.Models.dtos import GAME_DTO

# spi = spider(ALLKEYSHOP_CONF())
spi = spider(ENEBA_CONF())

spi.scraping_game("Dragon")
