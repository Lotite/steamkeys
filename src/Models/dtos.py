from datetime import date , datetime

class GAME_DTO:
    price:int
    name:str
    source_url:str
    source_web:str
    register_time:date
    
    
    def __init__(self):
        self.register_time = datetime.now().strftime("%Y-%m-%d")
    
    def to_dict(self):
        return self.__dict__
