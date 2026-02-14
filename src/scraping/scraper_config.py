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