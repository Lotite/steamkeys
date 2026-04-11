import undetected_chromedriver as uc
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from urllib3.exceptions import ProtocolError
from http.client import RemoteDisconnected
import time
import tempfile
import shutil
from src.utils.loger import Logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from abc import ABC, abstractmethod 
from src.utils.kafka import *
from json import dumps
import re
from concurrent.futures import ProcessPoolExecutor, as_completed
from src.steam.steamRequest import scraping_steam_game


### Orquestrador del scraping
class I_CONF(ABC):    
    
    @abstractmethod
    def buid_url(self, query: str) -> str:
        ...

    @property
    @abstractmethod
    def card_container_selector(self) -> str:
        ...
    
    
    @property
    @abstractmethod
    def source_web(self) -> str:
        ...
    
    
    @property
    @abstractmethod
    def next_page_selector(self) -> str:
        ...
    
    
    
    @property
    @abstractmethod
    def propietes_selector(self) -> dict[str, str]:
        ...
    
    @abstractmethod
    def create_dto(self)->object:
        ...
    
    
    def base_query_builder(self,query:str,space="%20"):
        query = re.sub(r"(?<=\S)\s+(?=\S)", space, query)  
        query = re.sub(r"\s+", "", query)
        return query;


    
    def make_dto(self,propertys:dict[str,str|float|int]):
        dto = self.create_dto()
        dto.state = 0;
        dto.source_web = self.source_web
        for key , value in propertys.items():
            setattr(dto, key, value)
        return dto
    


class spider:
    __SCRAPING_TIMEOUT_SECONDS = 60

    def __init__(self, orq:I_CONF,hidden:bool=True,log=True):
        self.__orq = orq
        self.__hidden = hidden
        self.__create_log=log;
        self.__kafka_producer = create_producer()
        self.__started_at = 0.0

    def __create_nav(self):
        options = uc.ChromeOptions()
        profile_dir = tempfile.mkdtemp(prefix="steamkeys-chrome-")

        if self.__hidden :
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

        options.add_argument("--disable-gpu")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36"
        )

        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--lang=es-ES")
        options.add_argument("--blink-settings=imagesEnabled=true")
        options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-sync")
        options.add_argument(f"--user-data-dir={profile_dir}")
        options.add_argument("--remote-debugging-port=0")
        driver = uc.Chrome(options=options, version_main=146)
        setattr(driver, "_steamkeys_profile_dir", profile_dir)
        driver.set_page_load_timeout(45)

        return driver

    def __close_nav(self, driver: WebDriver | None):
        if driver is None:
            return

        try:
            driver.quit()
        except Exception:
            pass

        try:
            driver.service.stop()
        except Exception:
            pass

        profile_dir = getattr(driver, "_steamkeys_profile_dir", None)
        if profile_dir:
            shutil.rmtree(profile_dir, ignore_errors=True)

    def __comprobar_tiempo(self):
        if time.monotonic() - self.__started_at >= self.__SCRAPING_TIMEOUT_SECONDS:
            raise Exception(f"Tiempo finalizado : {self.__SCRAPING_TIMEOUT_SECONDS} segundos")


    def SendDTO(self,dto:object):
        sendMessage(self.__kafka_producer,"SteamKeys",dto.source_web,dumps(dto.to_dict()))

    def __extractor(self, driver:WebDriver):
        dtos = []
        while True:
            try:
                self.__comprobar_tiempo()
                cards = self.__get_elements(driver,self.__orq.card_container_selector)
            
                dtos += [self.__extract_game_info(card) for card in cards]
                
                if not self.__next_page(driver):
                    break
            except EmptyResult as e:
                self.__log.add(f"Scraping cortado : {e}")
                print(f"Scraping cortado: {e}")
                break
            
        return dtos
    
    def __extract_game_info(self, card: WebElement):
        game_info = {}
        
        for property , selector in self.__orq.propietes_selector.items():
            game_info[property] = self.__extract_transform(card,selector)
        dto = self.__orq.make_dto(game_info)
        self.__log.add(f"Se extrajo este juego : {dto.__dict__}")
        self.SendDTO(dto=dto)
        return dto;
    
    
    

    def __extract_transform(self, card: WebElement, selector: str):
        element = self.__get_element(card, selector, 0.1)
        if element is None:
            raise EmptyResult(f"No se encontro {selector} en el card")

        tag_name = element.tag_name.lower()
        if tag_name == "a":
            href = element.get_attribute("href")
            if href:
                return href

        raw = element.text.strip()

        def clean_and_convert_to_number(text):
            cleaned_text = text
            currency_symbols = ["€", "$", "£", "¥", "₹", "₽", "₩", "₺", "%", "-"]
            for symbol in currency_symbols:
                cleaned_text = cleaned_text.replace(symbol, "")
            cleaned_text = cleaned_text.strip()

            is_negative = False
            if cleaned_text.startswith("-") and cleaned_text[1:].replace(".", "", 1).replace(",", "", 1).isdigit():
                is_negative = True
                cleaned_text = cleaned_text[1:]

            if cleaned_text.isdigit():
                return int(cleaned_text) * (-1 if is_negative else 1)

            num_commas = cleaned_text.count(",")
            num_periods = cleaned_text.count(".")

            if num_commas == 1 and num_periods == 0:
                cleaned_text = cleaned_text.replace(",", ".")
            elif num_periods == 1 and num_commas == 0:
                pass
            elif num_commas > 0 and num_periods > 0:
                if cleaned_text.rfind(",") > cleaned_text.rfind("."):
                    cleaned_text = cleaned_text.replace(".", "")
                    cleaned_text = cleaned_text.replace(",", ".")
                else:
                    cleaned_text = cleaned_text.replace(",", "")

            try:
                return float(cleaned_text) * (-1 if is_negative else 1)
            except ValueError:
                return None

        number_value = clean_and_convert_to_number(raw)
        if number_value is not None:
            return number_value

        return raw
    
    
    
    def __go_to(self, driver, url: str):
        self.__comprobar_tiempo()
        driver.get(url)
        self.__scroll_to_bottom(driver)
    
    def __next_page(self,driver:WebDriver):
        self.__comprobar_tiempo()
        time.sleep(0.3)
        try:
            button = self.__get_element(driver, self.__orq.next_page_selector)
            self.__click(driver,self.__orq.next_page_selector)
            if button:
                WebDriverWait(driver, 5).until(EC.staleness_of(button))
            
            time.sleep(0.5)
            self.__scroll_to_bottom(driver)
            self.__log.add(f"Se pudo hacer click a boton next page:{driver.current_url}")
            return True
        except Exception as e:
            self.__log.add(f"No se encontro el boton next page o no es clickeable: {e}")
            return False
    


    def __click(self, driver: WebDriver, selector: str, max_time=10):
        self.__comprobar_tiempo()
        button = self.__get_element(driver, selector, max_time=max_time)

        WebDriverWait(driver, max_time).until(
            EC.visibility_of(button)
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
            button
        )

        WebDriverWait(driver, max_time).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )

        try:
            button.click()
            return
        except:
            pass

        try:
            ActionChains(driver).move_to_element(button).click().perform()
            return
        except:
            pass

        driver.execute_script("arguments[0].click();", button)
        
    
        
    def __scroll_to_bottom(self, driver):
        self.__comprobar_tiempo()
        time.sleep(0.5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
    
    def __get_elements(self, driver: WebDriver, css_selector: str):
        self.__comprobar_tiempo()
        wait = WebDriverWait(driver, 3)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
            return driver.find_elements(By.CSS_SELECTOR, css_selector)
        except Exception as e:
            self.__log.add(f"No se encontro nungun elemento con el selector {css_selector}: {e}")
            return []


    
    def __get_element(self,driver:WebDriver|WebElement,css_selector:str,max_time=5):
        self.__comprobar_tiempo()
        wait = WebDriverWait(driver, max_time)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
            return driver.find_element(By.CSS_SELECTOR,css_selector)
        except Exception as e:
            self.__log.add(f"No se encontro nungun elemento con el selector {css_selector}: {e}")
            return None

    def scraping_game(self, query: str):
        with Logger(off= not self.__create_log) as log:
            self.__log = log;
            self.__started_at = time.monotonic()
            log.add(f"Iniciando test configuracion:{self.__orq.__class__}")
            try:
                url = self.__orq.buid_url(query)
                max_attempts = 3
                retry_errors = (
                    "Remote end closed connection without response",
                    "Connection aborted",
                    "disconnected: not connected to DevTools",
                    "session not created",
                    "chrome not reachable",
                )

                for attempt in range(1, max_attempts + 1):
                    driver = None
                    try:
                        driver = self.__create_nav()
                        self.__go_to(driver, url)
                        return self.__extractor(driver)
                    except Exception as e:
                        should_retry = (
                            attempt < max_attempts
                            and (
                                isinstance(e, (RemoteDisconnected, ProtocolError))
                                or any(text in str(e) for text in retry_errors)
                            )
                        )
                        if should_retry:
                            log.add(f"Fallo al iniciar navegador, reintento {attempt}/{max_attempts}: {e}")
                            time.sleep(min(2 * attempt, 5))
                            continue

                        log.add(f"El proceso se interumpio:{e}")
                        return None
                    finally:
                        self.__close_nav(driver)

                log.add("Se agotaron los reintentos de inicio")
                return None
            finally:
                self.__started_at = 0.0
                log.add("Se finalizo el scraping")


def scraping_game_store(steam_game:str,store_conf:I_CONF):
    spi = spider(store_conf,hidden=False)
    return spi.scraping_game(steam_game)


def _run_scraping_source(source:str, steam_game:str):
    from src.scraping.scraper_config import (
        ALLKEYSHOP_CONF,
        DRIFFLE_CONF,
        ENEBA_CONF,
        G2A_CONF,
    )

    stores = {
        "ENEBA": ENEBA_CONF,
        "G2A": G2A_CONF,
        "DRIFFLE": DRIFFLE_CONF,
        "ALLKEYSHOP": ALLKEYSHOP_CONF,
    }

    try:
        if source not in stores:
            raise ValueError(f"No existe configuracion para {source}")
        return source, scraping_game_store(steam_game, stores[source]())
    except Exception as exc:
        print(f"Error en {source} : {exc}")
        return source, None

def scrapin_game_stores(steam_game: str):
    sources = ["ENEBA", "G2A", "DRIFFLE", "ALLKEYSHOP"]
    results = {}

    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(_run_scraping_source, source, steam_game)
            for source in sources
        ]

        for future in as_completed(futures):
            source, data = future.result()
            results[source] = data

    return results
            
            
            
class EmptyResult(Exception):
    pass