import requests
import config
import json
from datetime import datetime
from typing import Optional


def get_destination_id(city: str) -> Optional[str]:
    url = "https://hotels4.p.rapidapi.com/locations/search"
    querystring = {"query": city, "locale": "ru_RU"}

    response = requests.request("GET", url, headers=config.headers, params=querystring)
    data = json.loads(response.text)
    try:
        return data['suggestions'][0]['entities'][0]['destinationId']
    except IndexError:
        return


def low_price(city: str, number_of_hotels: str) -> str:
    destination_id = get_destination_id(city)
    if not destination_id:
        return 'Город не найден'
    else:
        url = "https://hotels4.p.rapidapi.com/properties/list"
        date = datetime.now().date()
        querystring = {"adults1": "1",
                       "pageNumber": "1",
                       "destinationId": destination_id,
                       "pageSize": number_of_hotels,
                       "checkOut": date,
                       "checkIn": date,
                       "sortOrder": "PRICE",
                       "locale": "ru_RU",
                       "currency": "RUB"}

        response = requests.request("GET", url, headers=config.headers, params=querystring)
        data = json.loads(response.text)
        hotels_data = data['data']['body']['searchResults']['results']

        hotels_list = []
        rating = 0
        for i_hotel in hotels_data:
            rating += 1
            try:
                address = i_hotel['address']['streetAddress']
            except KeyError:
                address = 'Неизвестен'
            try:
                distance = i_hotel['landmarks'][0]['distance']
            except KeyError:
                distance = 'Неизвестно'
            try:
                price = i_hotel['ratePlan']['price']['current']
            except KeyError:
                price = 'Неизвестна'

            hotels_list.append('{rating} место\n'
                               'Отель: {name}.\n'
                               'Адрес: {address}.\n'
                               'Расстояние до центра города: {distance}.\n'
                               'Цена: {price}.'.format(rating=rating,
                                                       name=i_hotel['name'],
                                                       address=address,
                                                       distance=distance,
                                                       price=price))
        return '\n\n'.join(hotels_list)
