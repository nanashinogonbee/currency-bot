import json
import random
import socks
import socket
import telebot
import time

import date_currency_chart
import multi_currency_chart

from constants import TOKEN

print('locale init')
with open('locale.json') as locale_file:
    LOCALE = json.loads(locale_file.read())

PROXY_LIST = open('proxy_list.txt').readlines()
random_proxy = random.choice(PROXY_LIST).split(':')
print('proxy: {}:{}'.format(*random_proxy))

print('db init')

with open('params.json', 'r') as file_to_read:
    raw = file_to_read.read()
if raw:
    bot_params = json.loads(raw)
else:
    bot_params = {}

start = time.time()
WAIT_TIME = 10
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, *random_proxy)
print('connected.')

bot = telebot.TeleBot(TOKEN)

if time.time() - start >= WAIT_TIME:
    os.system('{} {}'.format(sys.argv[:2]))
else:
    print('started')


@bot.message_handler(commands=['start'])
def start(message):
    LANGS = ['English', 'Русский']
    BUTTONS = [telebot.types.KeyboardButton(lang) for lang in LANGS]
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(*BUTTONS)
    msg = bot.send_message(
            message.chat.id,
            '''Привет! Выбери язык из списка ниже:
Hello! Select a language from the list below:''',
            reply_markup=markup
            )
    bot.register_next_step_handler(msg, init_config)


def init_config(message):
    markup = telebot.types.ReplyKeyboardRemove(selective=False)
    if str(message.from_user.id) not in bot_params.keys():
        bot_params.update({str(message.from_user.id): {
            'lang': message.text,
            'currencies': None
            }})
    else:
        bot_params[str(message.from_user.id)]['lang'] = message.text
    with open('params.json', 'w') as file_to_write:
        file_to_write.write(json.dumps(bot_params))

    bot.reply_to(
            message,
            LOCALE['successful_lang_setup'][message.text],
            reply_markup=markup
            )


@bot.message_handler(commands=['currencies'])
def set_currencies_prepare(message):
    msg = bot.send_message(
            message.chat.id,
            LOCALE['set_curr'][bot_params[str(message.from_user.id)]['lang']]
            )
    bot.register_next_step_handler(msg, set_currencies)


def set_currencies(message):
    currencies = message.text.split()
    bot_params[str(message.from_user.id)]['currencies'] = currencies
    with open('params.json', 'w') as file_to_write:
        file_to_write.write(json.dumps(bot_params))


@bot.message_handler(commands=['help'])
def help(message):
    # TODO: help msg
    pass


@bot.message_handler(commands=['chart'])
def chart(message):
    try:
        bot.send_message(
                message.chat.id,
                LOCALE['graph'][bot_params[str(message.from_user.id)]['lang']]
                )
        result = multi_currency_chart.make_chart(
            currency_list=bot_params[str(message.from_user.id)]['currencies']
            )
        bot.send_photo(message.chat.id, open(result, 'rb'))
    except Exception as e:
        print(e)
        bot.send_message(
                message.chat.id,
                LOCALE['ch_err'][bot_params[str(message.from_user.id)]['lang']]
                )


@bot.message_handler(commands=['date_chart'])
def date_chart_prepare(message):
    msg = bot.send_message(
            message.chat.id,
            LOCALE['sel_date'][bot_params[str(message.from_user.id)]['lang']]
            )
    bot.register_next_step_handler(msg, date_chart)


def date_chart(message):
    start_date, end_date = message.text.split()
    try:
        bot.send_message(
                message.chat.id,
                LOCALE['graph'][bot_params[str(message.from_user.id)]['lang']]
                )
        result = date_currency_chart.make_chart(
            currencies=bot_params[str(message.from_user.id)]['currencies'],
            start_date=start_date,
            end_date=end_date
            )
        bot.send_photo(message.chat.id, open(result, 'rb'))
    except Exception as e:
        print(e)
        bot.send_message(
                message.chat.id,
                LOCALE['ch_err'][bot_params[str(message.from_user.id)]['lang']]
                )


bot.polling()
