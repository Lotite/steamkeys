from src.steam.steam_spider import SteamSpider


limit = 1000
spider = SteamSpider(oculto=False)
spider.scrape_topsellers(limite=limit)