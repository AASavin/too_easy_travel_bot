from typing import Tuple, Optional


def price_range(message: str) -> Tuple[Optional[int], Optional[int]]:
    """Проверка, что введенные данные - числа, разделенные дефисом"""
    try:
        price_min, price_max = message.split('-')
        price_min, price_max = int(price_min), int(price_max)
        if price_min > price_max:
            raise ValueError

    except ValueError:
        return None, None

    else:
        return price_min, price_max


def distance_range(message: str) -> Tuple[Optional[float], Optional[float]]:
    """Проверка, что введенные данные - числа, которые можно перевести во float, разделенные дефисом"""
    try:
        distance_min, distance_max = message.split('-')
        distance_min = float(distance_min.replace(',', '.'))
        distance_max = float(distance_max.replace(',', '.'))
        if distance_min > distance_max:
            raise ValueError

    except ValueError:
        return None, None

    else:
        return distance_min, distance_max


def number_of_hotels(message: str) -> Optional[int]:
    """Проверка, что введенные данные - число от 1 до 25"""
    try:
        number = int(message)
        if not 0 < number <= 25:
            raise ValueError

    except ValueError:
        return None

    else:
        return number
