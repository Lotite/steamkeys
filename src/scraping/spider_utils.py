import undetected_chromedriver as uc
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import time


from abc import ABC, abstractmethod 
import re
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
    
    
    def base_query_builder(self,query:str):
        query = re.sub(r"(?<=\S)\s+(?=\S)", "%20", query)  
        query = re.sub(r"\s+", "", query)
        return query;


    
    def make_dto(self,propertys:dict[str,str|float|int]):
        dto = self.create_dto()
        dto.source_web = self.source_web
        for key , value in propertys.items():
            setattr(dto, key, value)
        return dto
    


class spider:
    def __init__(self, orq:I_CONF):
        self.__orq = orq


    def __create_nav(self):
        options = uc.ChromeOptions()

        # Tamaño de ventana realista
        # options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

        # Evitar aceleración por GPU
        options.add_argument("--disable-gpu")

        # Requerido en contenedores / Linux
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # User-Agent realista
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36"
        )


        # Desactivar extensiones
        options.add_argument("--disable-extensions")

        # Desactivar notificaciones
        options.add_argument("--disable-notifications")

        # Desactivar infobars
        options.add_argument("--disable-infobars")

        # Idioma realista
        options.add_argument("--lang=es-ES")

        # Cargar imágenes
        options.add_argument("--blink-settings=imagesEnabled=true")

        # Simular hardware realista
        options.add_argument("--disable-features=IsolateOrigins,site-per-process")

        # Crear navegador undetected
        driver = uc.Chrome(options=options)

        return driver


    def __extractor(self, driver:WebDriver):
        dtos = []
        while True:
            try:
                cards = self.__get_elements(driver,self.__orq.card_container_selector)
            
                dtos += [self.__extract_game_info(card) for card in cards]
                
                if not self.__next_page(driver):
                    break
            except EmptyResult as e:
                print(f"Scraping cordado: {e}")
                break
            
        return dtos
    
    def __extract_game_info(self, card: WebElement):
        game_info = {}
        
        for property , selector in self.__orq.propietes_selector.items():
            game_info[property] = self.__extract_transform(card,selector)
        return self.__orq.make_dto(game_info)
    
    
    

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

        # Función auxiliar para limpiar y convertir a número
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
        driver.get(url)
        self.__scroll_to_bottom(driver)
    
    def __next_page(self,driver:WebDriver):
        time.sleep(0.3)
        try:
            button = self.__get_element(driver,self.__orq.next_page_selector,max_time=10)
            button.click()
            time.sleep(0.3)
            self.__scroll_to_bottom(driver)
            return True
        except:
            return False
        
        
    def __scroll_to_bottom(self, driver):
        time.sleep(0.5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
    
    def __get_elements(self, driver: WebDriver, css_selector: str):
        wait = WebDriverWait(driver, 3)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
            return driver.find_elements(By.CSS_SELECTOR, css_selector)
        except:
            return []


    
    def __get_element(self,driver:WebDriver|WebElement,css_selector:str,max_time=5):
        wait = WebDriverWait(driver, max_time)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
            return driver.find_element(By.CSS_SELECTOR,css_selector)
        except:
            return None

    def scraping_game(self, query: str):
        with self.__create_nav() as driver:
            url = self.__orq.buid_url(query)
            self.__go_to(driver,url)
            return self.__extractor(driver)
            
            
            
class EmptyResult(Exception):
    pass