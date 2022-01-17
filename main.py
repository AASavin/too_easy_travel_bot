import telebot
import config
import utils
from telebot import types
from find_hotels import get_hotels


class Request:
    def __init__(self, command: str):
        self.command = command
        self.sort_order = None
        self.city = None
        self.price_min = None
        self.price_max = None
        self.distance_min = None
        self.distance_max = None
        self.number_of_hotels = None
        self.set_sort_order()

    def set_sort_order(self):
        if self.command == '/lowprice':
            self.sort_order = 'PRICE'

        elif self.command == '/highprice':
            self.sort_order = 'PRICE_HIGHEST_FIRST'
        else:
            self.sort_order = 'DISTANCE_FROM_LANDMARK'


bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(content_types=['text'])
def define_command(message):
    """Определение команды бота"""
    if message.text in ('/start', '/help'):
        # Отправка кнопок
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

    elif message.text in ('/lowprice', '/highprice', '/bestdeal'):
        request = Request(command=message.text)
        bot.send_message(message.chat.id, 'Введите город:')
        bot.register_next_step_handler(message, get_city, request=request)

    else:
        bot.send_message(message.chat.id, 'Такой команды нет. Если нужна помощь в управлении ботом - введите /help')


def get_city(message, request):
    """Получение города"""
    request.city = message.text
    if request.command == '/bestdeal':
        bot.send_message(message.chat.id, 'Введите минимальную и максимальную цены в рублях через дефис:')
        bot.register_next_step_handler(message, get_price, request=request)
    else:
        bot.send_message(message.chat.id, 'Введите количество отелей в рейтинге (не больше 25):')
        bot.register_next_step_handler(message, get_number, request=request)


def get_price(message, request):
    """Получение диапазона цен"""
    if message.text == '/stop':
        return

    # Проверка введенных цен, перевод строки в целочисленные значения
    request.price_min, request.price_max = utils.price_range(message.text)

    if not request.price_max:
        bot.send_message(message.chat.id, 'Неправильно введен диапазон. '
                                          'Введите минимальную и максимальную цены в рублях через дефис '
                                          '(Пример: 2000-5000). '
                                          'Если хотите попробовать другую команду, введите команду /stop')
        bot.register_next_step_handler(message, get_price, request=request)
    else:
        bot.send_message(message.chat.id, 'Введите минимальное и максимальное расстояния до центра в км через дефис:')
        bot.register_next_step_handler(message, get_distance, request=request)


def get_distance(message, request):
    """Получение диапазона расстояния от центра"""
    if message.text == '/stop':
        return

    # Проверка введенного интервала расстояния, перевод строки в вещественные числа
    request.distance_min, request.distance_max = utils.distance_range(message.text)

    if not request.distance_max:
        bot.send_message(message.chat.id, 'Неправильно введен диапазон. '
                                          'Введите минимальное и максимальное расстояния в км через дефис '
                                          '(Пример: 0-5,5). '
                                          'Если хотите попробовать другую команду, введите команду /stop')
        bot.register_next_step_handler(message, get_distance, request=request)
    else:
        bot.send_message(message.chat.id, 'Введите количество отелей в рейтинге (не больше 25):')
        bot.register_next_step_handler(message, get_number, request=request)


def get_number(message, request):
    """Получение количества отелей и вызов функции с рейтингом отелей"""
    if message.text == '/stop':
        return

    # Проверка, что введенные данные - число от 1 до 25, перевод строки в целое число
    request.number_of_hotels = utils.number_of_hotels(message.text)

    if not request.number_of_hotels:
        bot.send_message(message.chat.id, 'Нужно ввести целое число от 1 до 25. '
                                          'Если хотите попробовать другую команду, введите команду /stop')
        bot.register_next_step_handler(message, get_number, request=request)

    else:
        hotels = get_hotels(request)
        bot.send_message(message.chat.id, hotels)


bot.polling(none_stop=True, interval=0)
