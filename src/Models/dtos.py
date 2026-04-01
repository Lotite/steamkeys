from datetime import date , datetime

class GAME_DTO:
    _id:int
    steam_id: int
    name:str
    
    source_url:str
    source_web:str
    
    web_price:int
    steam_price:int
    register_time:date
    region:str
    
    genres: list
    reviews_score: float
    release_date: str
    
    state:int
    
    
    def __init__(self):
        self.register_time = datetime.now().strftime("%Y-%m-%d")
    
    def to_dict(self):
        return self.__dict__
