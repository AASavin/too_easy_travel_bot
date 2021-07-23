import requests
import config
import json
from datetime import datetime
from destination_id import get_destination_id


def sort_by_price(sort_order: str, city: str, number_of_hotels: str) -> str:
    """Формирование и возврат топа отелей в зависимости от цены"""
    # Получение id города и проверка существования города в базе
    destination_id = get_destination_id(city)
    if not destination_id:
        return 'Город не найден'

    # Формирование запроса
    url = "https://hotels4.p.rapidapi.com/properties/list"
    date = datetime.now().date()
    querystring = {"adults1": "1",
                   "pageNumber": "1",
                   "destinationId": destination_id,
                   "pageSize": number_of_hotels,
                   "checkOut": date,
                   "checkIn": date,
                   "sortOrder": sort_order,
                   "locale": "ru_RU",
                   "currency": "RUB",
                   }

    # Отправка запроса, подготовка данных
    response = requests.request("GET", url, headers=config.headers, params=querystring)
    data = json.loads(response.text)
    hotels_data = data['data']['body']['searchResults']['results']

    # Цикл по всем отелям в странице запроса
    hotels_list = []
    rating = 0
    for i_hotel in hotels_data:

        # Проверка на наличие всех нужных данных у отеля, если данные отсутствуют - они заменяются
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

        # Добавление отеля в список отелей
        rating += 1
        hotels_list.append('{rating} место.\n'
                           'Отель: {name}.\n'
                           'Адрес: {address}.\n'
                           'Расстояние до центра города: {distance}.\n'
                           'Цена: {price}.'.format(rating=rating,
                                                   name=i_hotel['name'],
                                                   address=address,
                                                   distance=distance,
                                                   price=price))

    # Формирование строки для ответа бота
    if not hotels_list:
        return 'Подходящие отели не найдены'
    return '\n\n'.join(hotels_list)
