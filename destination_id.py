import requests
import config
import json
import re
from typing import Optional, Tuple


def get_destination_id(city: str) -> [Tuple[Optional[str], Optional[str]]]:
    """Поиск города, возврат его id и названия города со страной"""
    # Формирование запроса
    url = "https://hotels4.p.rapidapi.com/locations/search"
    querystring = {"query": city, "locale": "ru_RU"}

    # Запрос, подготовка данных
    response = requests.request("GET", url, headers=config.headers, params=querystring)
    data = json.loads(response.text)

    # Получение и возврат destination_id и названия населенного пункта
    try:
        destination_id = data['suggestions'][0]['entities'][0]['destinationId']
        location = data['suggestions'][0]['entities'][0]["caption"]
        # Удаление тегов из названия населенного пункта
        location = re.sub(r'<.*?>', '', location)
        return destination_id, location
    except IndexError:
        return None, None
