import requests
import config
import json
from typing import Optional


def get_destination_id(city: str) -> Optional[str]:
    """Поиск города и возврат его id"""
    url = "https://hotels4.p.rapidapi.com/locations/search"
    querystring = {"query": city, "locale": "ru_RU"}

    response = requests.request("GET", url, headers=config.headers, params=querystring)
    data = json.loads(response.text)
    try:
        return data['suggestions'][0]['entities'][0]['destinationId']
    except IndexError:
        return
