import requests
import config
import json
from datetime import datetime
from destination_id import get_destination_id
from typing import List, Tuple, Optional
from utils import get_hotel_params


def get_hotels(request) -> str:
    """Получение id города и списка отелей"""
    # Получение destination id
    destination_id, location = get_destination_id(request.city)
    if not destination_id:
        return 'Город не найден'

    if request.command != '/bestdeal':
        hotels_list = get_hotels_page(request=request, destination_id=destination_id, page=1, rating_counter=0)[0]

    else:
        # Цикл проходит страницам, пока в списке отелей не наберется нужное число отелей
        next_page = 1
        rating_counter = 0
        hotels_list = []
        while True:
            hotels_list_add, next_page = get_hotels_page(request=request, destination_id=destination_id,
                                                         page=next_page, rating_counter=rating_counter)
            hotels_list.extend(hotels_list_add)
            rating_counter = len(hotels_list)
            if not next_page:
                break

    if not hotels_list:
        return '{location}\nПодходящие отели не найдены'.format(location=location)
    return '\n\n'.join((location, '\n\n'.join(hotels_list)))


def get_hotels_page(request, destination_id: str, page: int,
                    rating_counter: int) -> Tuple[List[str], Optional[int]]:
    """Получение топа отелей с одной страницы поиска"""

    url = "https://hotels4.p.rapidapi.com/properties/list"
    date = datetime.now().date()
    if request.command == '/bestdeal':
        page_size = '25'
    else:
        page_size = request.number_of_hotels
    querystring = {"adults1": '1',
                   "pageNumber": page,
                   "destinationId": destination_id,
                   "pageSize": page_size,
                   "checkOut": date,
                   "checkIn": date,
                   "sortOrder": request.sort_order,
                   "locale": 'ru_RU',
                   "currency": 'RUB',
                   "priceMin": request.price_min,
                   "priceMax": request.price_max,
                   'landmarkIds': 'center'}

    response = requests.request("GET", url, headers=config.headers, params=querystring)
    data = json.loads(response.text)
    hotels_data = data['data']['body']['searchResults']['results']

    hotels_list = []
    for i_hotel in hotels_data:
        # Поиск нужных данных у отеля, если данные отсутствуют - они отмечаются как неизвестные
        address, distance, price = get_hotel_params(i_hotel)

        if request.command == '/bestdeal':
            # Проверка, подходит ли отель по расположению от центра. Дистанция меньше - отель пропускается.
            # Больше - следующая страница для поиска не передается
            hotel_distance = float(distance.replace(',', '.').split()[0])
            if hotel_distance < request.distance_min:
                continue
            elif hotel_distance > request.distance_max:
                return hotels_list, None

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

        if request.command == '/bestdeal':
            # Если количество отелей в списке достигло запрашиваемого - следующая страница для поиска не передается
            if rating_counter == request.number_of_hotels:
                return hotels_list, None

    if request.command == '/bestdeal' and 'nextPageNumber' in data['data']['body']['searchResults']['pagination']:
        next_page = data['data']['body']['searchResults']['pagination']['nextPageNumber']
    else:
        next_page = None
    return hotels_list, next_page
