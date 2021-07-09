import telebot

TOKEN = '1856520108:AAHcdWFQ6HuYSqUFq1PiIW2-fnEeo5StNnQ'
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(content_types=['text'])
def say_hi(message):
    if message.text == '/hello-world':
        bot.send_message(message.chat.id, 'Привет, мир!')
    elif message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Привет!')
    else:
        bot.send_message(message.chat.id, 'К такому я ещё не готов 😥')


bot.polling(none_stop=True, interval=0)
