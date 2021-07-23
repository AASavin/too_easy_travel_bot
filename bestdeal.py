import requests
import config
import json
from datetime import datetime
from math import ceil
from destination_id import get_destination_id
from typing import List


def best_deal(city: str, price_min: str, price_max: str, distance_min: float, distance_max: float,
              number_of_hotels: str) -> str:
    """Получение id города и вызов get_hotels_list"""
    destination_id = get_destination_id(city)
    if not destination_id:
        return 'Город не найден'
    else:
        hotels_list = get_hotels_list(destination_id=destination_id, price_min=price_min, price_max=price_max,
                                      distance_min=distance_min, distance_max=distance_max,
                                      number_of_hotels=int(number_of_hotels))
        if not hotels_list:
            return 'Подходящие отели не найдены'
        return '\n\n'.join(hotels_list)


def get_hotels_list(destination_id: str, price_min: str, price_max: str, distance_min: float, distance_max: float,
                    number_of_hotels: int, page: int = 1, rating_counter: int = 0) -> List[str]:
    """Формирование и возврат топа отелей, наиболее подходящих по цене и расположению от центра"""
    # Формирование запроса
    url = "https://hotels4.p.rapidapi.com/properties/list"
    date = datetime.now().date()
    querystring = {"adults1": '1',
                   "pageNumber": str(page),
                   "destinationId": destination_id,
                   "pageSize": '25',
                   "checkOut": date,
                   "checkIn": date,
                   "sortOrder": 'DISTANCE_FROM_LANDMARK',
                   "locale": 'ru_RU',
                   "currency": 'RUB',
                   "priceMin": price_min,
                   "priceMax": price_max,
                   'landmarkIds': 'center'}

    # Отправка запроса, подготовка данных
    response = requests.request("GET", url, headers=config.headers, params=querystring)
    data = json.loads(response.text)
    hotels_data = data['data']['body']['searchResults']['results']

    # Определение максимального числа страниц
    total_count = data['data']['body']['searchResults']['totalCount']
    total_pages = ceil(int(total_count) / 25)

    # Цикл по всем отелям в странице запроса
    hotels_list = []
    for i_hotel in hotels_data:

        # Проверка на наличие всех нужных данных у отеля. Если данные отсутствуют - отель пропускается
        try:
            address = i_hotel['address']['streetAddress']
            distance = i_hotel['landmarks'][0]['distance']
            price = i_hotel['ratePlan']['price']['current']
        except KeyError:
            continue

        # Проверка, подходит ли отель по расположению от центра. Дистанция больше - формирование списка заканчивается
        float_distance = float(distance.replace(',', '.').split()[0])
        if float_distance < distance_min:
            continue
        if float_distance > distance_max:
            return hotels_list

        # Добавление отеля в список отелей
        rating_counter += 1
        hotels_list.append('{rating} место.\n'
                           'Отель: {name}.\n'
                           'Адрес: {address}.\n'
                           'Расстояние до центра города: {distance}.\n'
                           'Цена: {price}.'.format(rating=rating_counter,
                                                   name=i_hotel['name'],
                                                   address=address,
                                                   distance=distance,
                                                   price=price))

        # Если количество отелей в списке достигло запрашиваемого - формирование списка заканчивается
        if len(hotels_list) == number_of_hotels:
            return hotels_list

    # Рекурсивный вызов функции для поиска на следующей странице
    if page < total_pages:
        hotels_list.extend(get_hotels_list(destination_id=destination_id, price_min=price_min, price_max=price_max,
                                           distance_min=distance_min, distance_max=distance_max,
                                           number_of_hotels=number_of_hotels-len(hotels_list), page=page+1,
                                           rating_counter=rating_counter))

    # Если закончились страницы или функция прошла через рекурсию - формирование списка заканчивается
    return hotels_list
