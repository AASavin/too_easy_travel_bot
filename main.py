import telebot
import config
from telebot import types
from sort_by_price import sort_by_price
from bestdeal import best_deal

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(content_types=['text'])
def define_command(message):
    """Определение команды бота"""
    if message.text in ('/start', '/help'):
        # Кнопки отправляются каждый раз, когда вводится /help на случай, если клавиатура пропадет
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        bttn_1 = types.KeyboardButton('/lowprice')
        bttn_2 = types.KeyboardButton('/highprice')
        bttn_3 = types.KeyboardButton('/bestdeal')
        bttn_4 = types.KeyboardButton('/help')
        markup.add(bttn_1, bttn_2, bttn_3, bttn_4)
        bot.send_message(message.chat.id, 'Команды бота:\n'
                                          '/lowprice - вывод самых дешёвых отелей в городе\n'
                                          '/highprice — вывод самых дорогих отелей в городе\n'
                                          '/bestdeal — вывод отелей, '
                                          'наиболее подходящих по цене и расположению от центра', reply_markup=markup)

    elif message.text == '/lowprice':
        bot.send_message(message.chat.id, 'Введите город:')
        bot.register_next_step_handler(message, get_city, sort_order='PRICE')

    elif message.text == '/highprice':
        bot.send_message(message.chat.id, 'Введите город:')
        bot.register_next_step_handler(message, get_city, sort_order='PRICE_HIGHEST_FIRST')

    elif message.text == '/bestdeal':
        bot.send_message(message.chat.id, 'Введите город:')
        bot.register_next_step_handler(message, get_city, sort_order='DISTANCE_FROM_LANDMARK')

    else:
        bot.send_message(message.chat.id, 'Такой команды нет. Если нужна помощь в управлении ботом - введите /help')


def get_city(message, sort_order):
    """Получение города"""
    # Для команды /bestdeal. Переход в get_price
    if sort_order == 'DISTANCE_FROM_LANDMARK':
        bot.send_message(message.chat.id, 'Введите минимальную и максимальную цены в рублях через дефис:')
        bot.register_next_step_handler(message, get_price, sort_order=sort_order, city=message.text)
    # Для остальных команд. Переход в get_number
    else:
        bot.send_message(message.chat.id, 'Введите количество отелей в рейтинге (не больше 25):')
        bot.register_next_step_handler(message, get_number, sort_order=sort_order, city=message.text)


def get_price(message, city, sort_order):
    """Получение диапазона цен"""
    # Для выхода, если пользователь не может справиться с вводом
    if message.text.lower() == 'стоп':
        return

    # Проверка, что введенные данные - числа, разделенные дефисом
    try:
        price_min, price_max = message.text.split('-')
        if int(price_min) > int(price_max):
            raise ValueError

    except ValueError:
        # Вызов себя для очередной попытки ввода
        bot.send_message(message.chat.id, 'Неправильно введен диапазон. '
                                          'Введите минимальную и максимальную цены в рублях через дефис '
                                          '(Пример: 2000-5000). '
                                          'Если хотите попробовать другую команду, введите "стоп"')
        bot.register_next_step_handler(message, get_price, city=city, sort_order=sort_order)

    else:
        # Переход в get_distance
        bot.send_message(message.chat.id, 'Введите минимальное и максимальное расстояния до центра в км через дефис:')
        bot.register_next_step_handler(message, get_distance, city=city, sort_order=sort_order,
                                       price_min=price_min, price_max=price_max)


def get_distance(message, city, sort_order, price_min, price_max):
    """Получение диапазона расстояния от центра"""
    # Для выхода, если пользователь не может справиться с вводом
    if message.text.lower() == 'стоп':
        return

    # Проверка, что введенные данные - числа, которые можно перевести во float, разделенные дефисом
    try:
        distance_min, distance_max = message.text.split('-')
        distance_min = float(distance_min.replace(',', '.'))
        distance_max = float(distance_max.replace(',', '.'))
        if distance_min > distance_max:
            raise ValueError

    except ValueError:
        # Вызов себя для очередной попытки ввода
        bot.send_message(message.chat.id, 'Неправильно введен диапазон. '
                                          'Введите минимальное и максимальное расстояния в км через дефис '
                                          '(Пример: 0-5,5). '
                                          'Если хотите попробовать другую команду, введите "стоп"')
        bot.register_next_step_handler(message, get_distance, city=city, sort_order=sort_order,
                                       price_min=price_min, price_max=price_max)

    else:
        # Переход в get_number
        bot.send_message(message.chat.id, 'Введите количество отелей в рейтинге (не больше 25):')
        bot.register_next_step_handler(message, get_number, city=city, sort_order=sort_order,
                                       price_min=price_min, price_max=price_max,
                                       distance_min=distance_min, distance_max=distance_max)


def get_number(message, sort_order, city, price_min=None, price_max=None, distance_min=None, distance_max=None):
    """Получение количества отелей и вызов функции с рейтингом отелей"""
    # Для выхода, если пользователь не может справиться с вводом
    if message.text.lower() == 'стоп':
        return
    # Проверка, что введенные данные - число от 1 до 25
    try:
        number = int(message.text)
        if not 0 < number <= 25:
            raise ValueError

    except ValueError:
        # Вызов себя для очередной попытки ввода
        bot.send_message(message.chat.id, 'Нужно ввести целое число от 1 до 25. '
                                          'Если хотите попробовать другую команду, введите "стоп"')
        bot.register_next_step_handler(message, get_number, city=city, sort_order=sort_order,
                                       price_min=price_min, price_max=price_max,
                                       distance_min=distance_min, distance_max=distance_max)

    else:
        # Команда /bestdeal
        if sort_order == 'DISTANCE_FROM_LANDMARK':
            hotels = best_deal(city=city, price_min=price_min, price_max=price_max,
                               distance_min=distance_min, distance_max=distance_max, number_of_hotels=int(message.text))
        # Остальные команды
        else:
            hotels = sort_by_price(sort_order=sort_order, city=city, number_of_hotels=message.text)

        bot.send_message(message.chat.id, hotels)


bot.polling(none_stop=True, interval=0)
