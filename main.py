import telebot
import config
from lowprice import low_price

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(content_types=['text'])
def define_command(message):
    if message.text == '/help':
        bot.send_message(message.chat.id, 'Команды бота:\n'
                                          '/lowprice - вывод самых дешёвых отелей в городе\n'
                                          '/highprice — вывод самых дорогих отелей в городе\n'
                                          '/bestdeal — вывод отелей, '
                                          'наиболее подходящих по цене и расположению от центра')

    elif message.text == '/lowprice':
        bot.send_message(message.chat.id, 'Введите город:')
        bot.register_next_step_handler(message, get_city)

    else:
        bot.send_message(message.chat.id, 'Такой команды нет. Если нужна помощь в управлении ботом - введите /help')


def get_city(message):
    city = message.text
    bot.send_message(message.chat.id, 'Введите количество отелей в рейтинге (не больше 25):')
    bot.register_next_step_handler(message, get_number, city)


def get_number(message, city):
    hotels = low_price(city=city, number_of_hotels=message.text)
    bot.send_message(message.chat.id, hotels)


bot.polling(none_stop=True, interval=0)
