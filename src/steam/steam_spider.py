import time
import json
from selenium.webdriver.common.by import By
from utils.kafka import create_producer, sendMessage
from scraping.spider_utils import scrapin_game_stores
from steam.steamRequest import GetSteamInfoById
from utils.driver import create_driver, destroy_driver

class SteamSpider:
    def __init__(self, oculto=True):
        self.oculto = oculto
        self.producer = create_producer()
        self.ids_vistos = set()
        self.url_steam = "https://store.steampowered.com/search/?filter=topsellers&ndl=1&hidef2p=1"

    def scrape_topsellers(self, limite=100):
        print("Iniciando escraping")
        driver, dir_perfil = create_driver(headless=self.oculto)
        lote_actual = []
        contador_total = 0

        try:
            driver.get(self.url_steam)
            time.sleep(3) 
            while contador_total < limite:
                # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                filas = driver.find_elements(By.CSS_SELECTOR, "a.search_result_row")
                
                for fila in filas:
                    if contador_total >= limite:
                        break
                        
                    steam_id_raw = fila.get_attribute("data-ds-appid")
                    if not steam_id_raw or steam_id_raw in self.ids_vistos:
                        continue

                    try:
                        full_info = GetSteamInfoById(int(steam_id_raw))
                        if not full_info:
                            continue

                        # Filtramos solo los campos requeridos en inglés simplificado
                        juego_simplificado = {
                            "name": full_info["name"],
                            "steam_id": full_info["steam_id"],
                            "genres": full_info["genres"],
                            "price": full_info["steam_price"]
                        }

                        # Envío inmediato a Kafka (Diccionario JSON simplificado)
                        sendMessage(self.producer, "SteamGames", "STEAM", json.dumps(juego_simplificado))
                        
                        # Eliminamos el elemento del DOM para no volver a procesarlo y liberar memoria
                        driver.execute_script("arguments[0].remove();", fila)
                        
                        self.ids_vistos.add(steam_id_raw)
                        lote_actual.append(juego_simplificado)
                        contador_total = len(lote_actual)
                        
                        print(f" > [{contador_total}] Enviado: {juego_simplificado['name']} ({juego_simplificado['price']}€)")

                        if len(lote_actual) >= 100:
                            self._procesar_keys_lote(lote_actual)
                            lote_actual = []

                    except:
                        continue

        finally:
            destroy_driver(driver, dir_perfil)

    def _procesar_keys_lote(self, lote):
        for juego in lote:
            scrapin_game_stores(juego['name'])


if __name__ == "__main__":
    limit = 1000
    spider = SteamSpider(oculto=False)
    spider.scrape_topsellers(limite=limit)
