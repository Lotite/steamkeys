from pathlib import Path
import sys

if "src" not in sys.modules and str(Path(__file__).resolve().parents[2]) not in sys.path:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

import random
import re
from concurrent.futures import ThreadPoolExecutor
from json import dumps

import requests
from confluent_kafka import Producer
from pandas import DataFrame, Series

from Models.dtos import GAME_DTO
from utils.kafka import create_producer, sendMessage

RAWG_KEY = "ce849f6ddcf94229a5a7669f0b229eba"




def GetGameList(size:int=40) -> Series:
    page = random.randint(1,10000/size)
    url = f"https://api.rawg.io/api/games?key={RAWG_KEY}&stores=1&page_size={size}&page={page}"
    resul = requests.get(url, timeout=10).json()
    steam_games = DataFrame(resul["results"])["slug"]
    return get_all_games_info(steam_games)

def base_query_builder(query:str,space="%20"):
    query = re.sub(r"(?<=\S)\s+(?=\S)", space, query)  
    query = re.sub(r"\s+", "", query)
    return query;

def GetGameName(scrapin_name:str):
    url = f"https://store.steampowered.com/api/storesearch/?term={scrapin_name}&l=english&cc=US"
    try:
        resul = requests.get(url, timeout=10).json()
        return resul["items"][0]["name"]
    except:
        return scrapin_name



def GetSteamId(scrapin_name:str)->int:
    game_name = GetGameName(scrapin_name)
    url = f"https://store.steampowered.com/api/storesearch/?term={base_query_builder(game_name)}&l=spanish&cc=ES"
    try:
        resul = requests.get(url, timeout=10).json()
        
        return resul["items"][0]["id"]
    except Exception:
        return None


def get_all_games_info(steam_games):
    producer = create_producer()
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(lambda name: GetSteamInfoByName(name, producer), steam_games))
    return DataFrame(results).dropna()


def GetSteamInfoById(steam_id:int):
    url = f"https://store.steampowered.com/api/appdetails?appids={steam_id}&cc=es"
    try:
        result = requests.get(url, timeout=20).json()
        result = result[str(steam_id)]["data"]
        steam_info = {}
        price_overview = result.get("price_overview", {})
        steam_info["steam_id"] = steam_id
        steam_info["name"] = result["name"]
        steam_info["steam_price"] = price_overview.get("final", 0) / 100
        steam_info["web_price"] = price_overview.get("initial", 0) / 100
        steam_info["discount_percent"] = price_overview.get("discount_percent", 0)
        steam_info["is_in_discount"] = steam_info["discount_percent"] > 0
        steam_info["genres"] = [genre["description"] for genre in result.get("genres", [])]
        steam_info["release_date"] = result.get("release_date", {}).get("date")
        steam_info["source_web"] = "STEAM"
        steam_info["source_url"] = f"https://store.steampowered.com/app/{steam_id}"
        steam_info["state"] = 0
        return steam_info
    except Exception:
        return {}

def _build_steam_dto(steam_info:dict) -> GAME_DTO | None:
    if not steam_info:
        return None

    dto = GAME_DTO()
    for key, value in steam_info.items():
        setattr(dto, key, value)
    return dto


def GetSteamInfoByName(name_game:str,producer:Producer|None=None):
    steam_id = GetSteamId(name_game)
    if steam_id is None:
        return {}
    steam_info = GetSteamInfoById(steam_id)
    if steam_info and producer is not None:
        print(steam_info["name"])
        sendMessage(producer, "SteamGames", steam_info["source_web"], dumps(steam_info))
    return steam_info


def scraping_steam_game(name_game:str):
    producer = create_producer()
    steam_info = GetSteamInfoByName(name_game, producer)
    return _build_steam_dto(steam_info)
