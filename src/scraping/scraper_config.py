from src.scraping.spider_utils import I_CONF
from src.Models.dtos import GAME_DTO


#TODO: Añadir la extracion de la region en ENEBA G2A y ALLKEYSHOP, probar DRIFFLE

class ENEBA_CONF(I_CONF):
    
    def buid_url(self, query):
        return "https://www.eneba.com/es/store/all?drms[]=steam&page=1&text=" + self.base_query_builder(query);
    
    
    @property
    def source_web(self) -> str:
        return "ENEBA"
    
    @property
    def card_container_selector(self)->str:
        return ".JZCH_t > .pFaGHa";
    
    @property
    def next_page_selector(self)->str:

        return "li.rc-pagination-next";
    
    
    @property
    def propietes_selector(self) -> dict[str, str]:
        return {
            "name" : "div.lirayz > span",
            "steam_price":"div.VkR9uM > span > span",
            "source_url" : "div._vfaJQ > a",
            "region" : ".Pm6lW1"
        }
    
    def create_dto(self)->GAME_DTO:
        return GAME_DTO()   
    
class G2A_CONF(I_CONF):
    
    def buid_url(self, query):
        return "https://www.g2a.com/es/category/gaming-c1?f%5Bplatform%5D%5B0%5D=1&query=" + self.base_query_builder(query);

    @property
    def source_web(self) -> str:
        return "G2A"


    @property
    def card_container_selector(self)->str:
        return ".flex.w-full.flex-col.px-6.py-4";

    
    @property
    def next_page_selector(self)->str:
        return "nav > a";


    
    @property
    def propietes_selector(self) -> dict[str, str]:
        return {
            "name" : "h3",
            "steam_price":".text-price-2xl",
            "source_url" : "a",
            "region":".text-foreground-success-default.flex.gap-4"
        }

    def create_dto(self)->GAME_DTO:
        return GAME_DTO()
    
class ALLKEYSHOP_CONF(I_CONF):
    
    def buid_url(self, query):
        return "https://www.allkeyshop.com/blog/en-us/products/?search_name=" + self.base_query_builder(query,"+");
    
    
    @property
    def source_web(self) -> str:
        return "ALLKEYSHOP"
    
    @property
    def card_container_selector(self)->str:
        return "div.grid.grid-view.grid-cols-\\[200px\\].min-\\[376px\\]\\:grid-cols-fill.svelte-1o73xps > div";
    
    @property
    def next_page_selector(self)->str:

        return "nav > button:nth-child(3)";
    
    
    @property
    def propietes_selector(self) -> dict[str, str]:
        return {
            "name" : "p",
            "steam_price":"a span",
            "source_url" : "a"
        }
    
    def create_dto(self)->GAME_DTO:
        return GAME_DTO()
    
    
    
class DRIFFLE_CONF(I_CONF):
    
    def buid_url(self, query):
        return "https://driffle.com/store?D=Steam&q=" + self.base_query_builder(query);
    
    
    @property
    def source_web(self) -> str:
        return "DRIFFLE"
    
    @property
    def card_container_selector(self)->str:
        return "div.sc-4a6a0f6d-4.cAGifT > div";
    
    @property
    def next_page_selector(self)->str:

        return "div.sc-8f4e99c3-0.heFYPP > div:nth-last-child(2)";
    
    
    @property
    def propietes_selector(self) -> dict[str, str]:
        return {
            "name" : "span.sc-e6e4f92a-12",
            "steam_price":".sc-e6e4f92a-20",
            "source_url" : "a",
            "region" : ".sc-e6e4f92a-15"
        }
    
    def create_dto(self)->GAME_DTO:
        return GAME_DTO()   
        