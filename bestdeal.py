import requests
import config
import json
from datetime import datetime
from destination_id import get_destination_id
from typing import List, Tuple, Optional


def best_deal(city: str, price_min: str, price_max: str, distance_min: float, distance_max: float,
              number_of_hotels: int) -> str:
    """Получение id города и списка отелей"""
    # Получение destination id
    destination_id, location = get_destination_id(city)
    if not destination_id:
        return 'Город не найден'

    # Цикл проходит страницам, пока в списке отелей не наберется нужное число отелей
    next_page = 1
    rating_counter = 0
    hotels_list = []
    while True:
        hotels_list_add, next_page, rating_counter = get_hotels_list(destination_id=destination_id, price_min=price_min,
                                                                     price_max=price_max, distance_min=distance_min,
                                                                     distance_max=distance_max,
                                                                     number_of_hotels=
                                                                     number_of_hotels - len(hotels_list),
                                                                     page=next_page, rating_counter=rating_counter)
        hotels_list.extend(hotels_list_add)
        # Выход из цикла, если следующей страницы нет
        if not next_page:
            break

    # Возврат строки, сформированной из названия города и списка отелей
    if not hotels_list:
        return '{location}\nПодходящие отели не найдены'.format(location=location)
    return '\n\n'.join((location, '\n\n'.join(hotels_list)))


def get_hotels_list(destination_id: str, price_min: str, price_max: str, distance_min: float,
                    distance_max: float, number_of_hotels: int, page: int,
                    rating_counter: int) -> Tuple[List[str], Optional[int], int]:
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

    # Проверка, есть ли следующая страница для поиска
    if 'nextPageNumber' in data['data']['body']['searchResults']['pagination']:
        next_page = data['data']['body']['searchResults']['pagination']['nextPageNumber']
    else:
        next_page = None

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

        # Проверка, подходит ли отель по расположению от центра. Дистанция больше - следующая страница не передается
        float_distance = float(distance.replace(',', '.').split()[0])
        if float_distance < distance_min:
            continue
        if float_distance > distance_max:
            return hotels_list, None, rating_counter

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

        # Если количество отелей в списке достигло запрашиваемого - следующая страница не передается
        if len(hotels_list) == number_of_hotels:
            return hotels_list, None, rating_counter

    # Возврат списка, если цикл по отелям на странице прошел до конца
    return hotels_list, next_page, rating_counter
