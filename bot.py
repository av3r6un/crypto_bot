import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import time
import initialise
import send_message as sm
import pymysql.cursors
import babel.numbers as bn
import schedule
from config import Config as cfg


API = cfg.API_KEY
b = telebot.TeleBot(API)

con = pymysql.connect(host=cfg.HOST,
                      user=cfg.USER,
                      password=cfg.PASSWORD,
                      database=cfg.DATABASE,
                      cursorclass=pymysql.cursors.DictCursor)


@b.message_handler(commands=['start'])
def welcome(m):
    my_firstName = '@CryptoMemoryBot'
    b.send_message(m.chat.id, f"Привет, меня зовут {my_firstName}!\nЯ соберу информацию об интересующих тебя монетах.")
    time.sleep(1)
    b.send_message(m.chat.id, "Чтоб настроить меня напиши /settings")
    try:
        with con.cursor() as cursor:
            sql = "SELECT `user_id` FROM `users_choice`"
            cursor.execute(sql)
            res = cursor.fetchone()
        if res is None:
            with con.cursor() as cursor:
                sql = "INSERT INTO `users_choice` (`user_id`, `username`, `tokens`, `currency`, `period`, `start_time`) " \
                      "VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (m.from_user.id, m.from_user.first_name, '', '', 0, datetime.now().strftime("%H:%M:%S")))
            con.commit()
            print('Пользователь успешно добавлен!')
        elif res['user_id'] == m.from_user.id:
            print('Пользователь существует!')
        else:
            print('Произошла ошибка во время запроса. Повторите попытку позже.')
    except Exception as _ex:
        print(f"[INFO 1]: Ошибка {_ex}")


@b.message_handler(commands=['settings'])
def add(m):
    b.send_message(m.chat.id, "Тебе нужно писать по очереди название либо сокращения нужных токенов. Я буду "
                              "проверять их по своей базе. Если они буду совпадать, я их автоматически добавлю, "
                              "если нет, то я попрошу тебя изменить ключ поиска и предложу возможные варианты.")
    time.sleep(1)
    b.register_next_step_handler(m, search_coin)


def search_coin(m):
    req = m.text
    if req.lower() == 'exit':
        b.send_message(m.chat.id, "Монеты успешно добавлены. Давай выберем как часто ты хочешь получать уведомления.")
        b.send_message(m.chat.id, "Выбери временной диапазон:", reply_markup=gen_markup_for_time())
    else:
        slug = initialise.find_el(req)
        if slug:
            try:
                with con.cursor() as cursor:
                    sql = "SELECT `tokens` FROM `users_choice` WHERE `user_id` = %s"
                    cursor.execute(sql, (m.from_user.id,))
                    res = cursor.fetchone()
            except Exception as _ex:
                print(f"[INFO 2]: Ошибка {_ex}")
            if res['tokens'] == '':
                change_list = slug
                b.send_message(m.chat.id, 'Я добавил монету ' + req + ' (' + slug + ') в избранное')
            else:
                avTokens = res['tokens'].split(', ')
                availTokens = ', '.join(initialise.replace(avTokens)) + ', ' + req
                time.sleep(1)
                b.send_message(m.chat.id, "Монеты, которые ты уже добавил: " + availTokens)
                time.sleep(1)
                b.send_message(m.chat.id, "Если ты хочешь добавить ещё монеты просто напиши их название. Если нет, напиши exit")
                change_list = res['tokens'] + ", " + slug
            update_table(change_list, m.from_user.id)
        else:
            print('Монета ' + req + " Не найдена! Попробуйте изменить запрос.")
            b.send_message(m.chat.id, 'Монета ' + req + " Не найдена! Попробуйте изменить запрос.")
    b.register_next_step_handler(m, search_coin)


def update_table(change_list, user_id):
    try:
        with con.cursor() as cursor:
            sql = "UPDATE `users_choice` SET `tokens` = %s WHERE `user_id` = %s"
            cursor.execute(sql, (change_list, user_id))
        con.commit()
    except Exception as _ex:
        print(f'[INFO 3]: Ошибка {_ex}')


def gen_markup_for_time():
    markup = InlineKeyboardMarkup()
    markup.row_width = 4
    markup.add(InlineKeyboardButton("1 час", callback_data="time_1"),
               InlineKeyboardButton("6 часов", callback_data="time_6"),
               InlineKeyboardButton("12 часов", callback_data="time_12"),
               InlineKeyboardButton("24 часа", callback_data="time_24"))
    return markup


@b.callback_query_handler(func=lambda first: True)
def callback_query_for_time(first):
    user_id = first.from_user.id
    cid = first.message.chat.id
    if first.data == "time_1":
        timing = 3600
        add_timing(timing, user_id)
        b.send_message(cid, "Отлично, я буду присылать тебе уведолмения каждый час!")
        time.sleep(1)
        b.send_message(cid, "Теперь выбери валюту в который будешь получать информацию:",
                       reply_markup=gen_markup_for_curr())
    elif first.data == "time_6":
        timing = 3600 * 6
        add_timing(timing, user_id)
        b.send_message(cid, "Отлично, я буду присылать тебе уведолмения каждые 6 часов!")
        time.sleep(1)
        b.send_message(cid, "Теперь выбери валюту в который будешь получать информацию:",
                       reply_markup=gen_markup_for_curr())
    elif first.data == "time_12":
        timing = 3600 * 12
        add_timing(timing, user_id)
        b.send_message(cid, "Отлично, я буду присылать тебе уведолмения каждые 12 часов!")
        time.sleep(1)
        b.send_message(cid, "Теперь выбери валюту в который будешь получать информацию:",
                       reply_markup=gen_markup_for_curr())
    elif first.data == "time_24":
        timing = 3600 * 24
        add_timing(timing, user_id)
        b.send_message(cid, "Отлично, я буду присылать тебе уведолмения каждые 24 часа!")
        time.sleep(1)
        b.send_message(cid, "Теперь выбери валюту в который будешь получать информацию:",
                       reply_markup=gen_markup_for_curr())
    elif first.data == 'curr_usd':
        curr = 'usd'
        set_currency(curr, user_id)
        time.sleep(1)
        b.send_message(cid, 'Сейчас я отправлю тебе первую информацию. С этого времени начнётся отсчёт.')
        time.sleep(2)
        send_message(cid, user_id)
    elif first.data == 'curr_btc':
        curr = 'btc'
        set_currency(curr, user_id)
        time.sleep(1)
        b.send_message(cid, 'Сейчас я отправлю тебе первую информацию. С этого времени начнётся отсчёт.')
        time.sleep(2)
        send_message(cid, user_id)


def add_timing(timing, user_id):
    date_start = datetime.now().strftime("%H:%M:%S")
    try:
        with con.cursor() as cursor:
            sql = "UPDATE `users_choice` SET `period` = %s, `start_time` = %s WHERE `user_id` = %s"
            cursor.execute(sql, (timing, date_start, user_id))
        con.commit()
    except Exception as _ex:
        print(f'[INFO 4]: Ошибка {_ex}')


def gen_markup_for_curr():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("USD", callback_data="curr_usd"),
               InlineKeyboardButton("BTC", callback_data="curr_btc"))
    return markup


def set_currency(currency, user_id):
    try:
        with con.cursor() as cursor:
            sql = "UPDATE `users_choice` SET `currency` = %s WHERE `user_id` = %s"
            cursor.execute(sql, (currency, user_id))
        con.commit()
    except Exception as _ex:
        print(f"[INFO 5]: Ошибка {_ex}")


@b.message_handler(commands=['rush'])
def rush_message(m):
    send_message(m.chat.id, m.from_user.id)


def send_message(cid, user_id):
    try:
        with con.cursor() as cursor:
            sql = "SELECT * FROM `users_choice` WHERE `user_id` = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
    except Exception as _ex:
        print(f"[INFO 6]: Ошибка {_ex}")
    answer_list = []
    answer = sm.request(result['tokens'].replace(' ', ''), result['currency'])
    for el in answer['data'].items():
        symbol = el[1]['symbol']
        price = bn.format_currency(round(el[1]['quote']['usd'.upper()]['price'], 2), "USD", locale='en_US')
        percent1H = round(el[1]['quote']['usd'.upper()]['percent_change_1h'], 1)
        percent24H = round(el[1]['quote']['usd'.upper()]['percent_change_24h'], 1)
        cap = bn.format_currency(round(el[1]['quote']['usd'.upper()]['market_cap'], 1), "USD", locale='en_US')
        a = f'{symbol}: {price}$ ({percent1H}%) [{percent24H}%]\nРыночная капитализация {symbol}: {cap}$' + '\n'
        answer_list.append(a)
    b.send_message(cid, '\n'.join(answer_list))
    return True


def fetchone(user_id):
    try:
        with con.cursor() as cursor:
            sql = "SELECT * FROM `users_choice` WHERE `user_id` = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
    except Exception as _ex:
        print(f"[INFO 6]: Ошибка {_ex}")
    return result


def ts():
    timestamp = datetime.now().strftime("%M")
    return timestamp


def send_mess():
    send_message(1039572834, 1039572834)


def scheduled_message_sender():
    data = fetchone(1039572834)
    userTime = ":" + str(data['time']).split(':')[1]
    schedule.every().hour.at(userTime).do(send_mess)
    while True:
        schedule.run_pending()
        time.sleep(1)


scheduled_message_sender()
b.infinity_polling()