from datetime import datetime
import os

class Logger:
    def __init__(self, name: str = None, folder: str = "logs",off=False):
        self.__off = off;
        
        if self.__off:
            return
        
        os.makedirs(folder, exist_ok=True)
        if name is None:
            name = "document_" + self.__get_time() + ".txt"
        path = os.path.join(folder, name)

        self.__file = open(path, mode="a")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.__off:
            return
        self.__file.close()

    def add(self, text: str):
        if self.__off:
            return
        time = f"({self.__get_time()}) "
        self.__file.write(time + text + "\n")

    def __get_time(self):
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")