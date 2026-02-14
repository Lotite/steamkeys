from datetime import date , datetime

class GAME_DTO:
    price:int
    name:str
    source_url:str
    source_web:str
    register_time:date = datetime.now().date
    
    
    def to_dict(self):
        return self.__dict__
