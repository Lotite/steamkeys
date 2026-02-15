from src.scraping.spider_utils import I_CONF
from src.Models.dtos import GAME_DTO


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
            "price":"div.VkR9uM > span > span",
            "source_url" : "div._vfaJQ > a"
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
        return "ul.iIAArv > li";

    
    @property
    def next_page_selector(self)->str:
        return "nav > a";


    
    @property
    def propietes_selector(self) -> dict[str, str]:
        return {
            "name" : "a > h3",
            "price":"div.font-bold.text-foreground.text-price-2xl",
            "source_url" : "a"
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
            "price":"a span",
            "source_url" : "a"
        }
    
    def create_dto(self)->GAME_DTO:
        return GAME_DTO()