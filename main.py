# Импортировать
import os
import telebot
from telebot import types
import config
from flask import Flask, request

# Токен и группа ID
APP_URL = f'https://omorjanovheroku.herokuapp.com/{config.tokenbot}'
bot = telebot.TeleBot(config.tokenbot)
server = Flask(__name__)

user_dict = {}
user_chats = 0


class User:
    def __init__(self, name):
        self.name = name
        self.age = None
        self.languages = None
        self.sex = None

        keys = ['will_learn', 'languages', 'want_admin']
        for key in keys:
            self.key = None


# При нажати на Телефон или /reg
@bot.message_handler(commands=['tell'])
def send_welcome1(message):
    try:
        chat_id = message.chat.id
        msg = bot.send_message(chat_id, "Введите ваше имя или никнейм:  ")
        bot.register_next_step_handler(msg, process_name_step)

        # Проверка
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = User(name)
        user_dict[chat_id] = user
        msg = bot.send_message(chat_id, 'Введи свой возраст: ')
        bot.register_next_step_handler(msg, process_want_lang_step)

    # Проверка
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_want_lang_step(message):
    try:
        chat_id = message.chat.id
        will_learn = message.text
        user = user_dict[chat_id]
        user.will_learn = will_learn
        msg = bot.send_message(chat_id, 'Ваш номер:')
        bot.register_next_step_handler(msg, process_language_step)

    # Проверка
    except Exception as e:
        bot.reply_to(message, '12!')


def process_language_step(message):
    try:
        chat_id = message.chat.id
        language = message.text
        user = user_dict[chat_id]
        user.languages = language

        msg = bot.send_message(chat_id, 'Вам позванить? ')
        bot.register_next_step_handler(msg, process_want_admin_step)

    # Проверка
    except Exception as e:
        bot.reply_to(message, 'Непредвиденная ошибка')


def process_want_admin_step(message):
    try:
        global user_chats

        chat_id = message.chat.id
        want_adm = message.text
        name = message.from_user.username
        name1 = message.from_user.first_name
        user = user_dict[chat_id]
        user.want_admin = want_adm
        bot.send_message(message.from_user.id, f'Ваше имя/(или никнейм) - {user.name} \n'
                         + f'Ваш возраст  -  {user.will_learn} \n'
                         + f'Ваш номер  -  {user.languages} \n'
                         + f'Вам позвонить  -  {user.want_admin}')

        markup = types.InlineKeyboardMarkup()
        site_btn = types.InlineKeyboardButton(text='Принять', callback_data='yes')
        site_btn1 = types.InlineKeyboardButton(text='Отклонить', callback_data='no')
        markup.add(site_btn, site_btn1)
        user_chats = message.from_user.id

        bot.send_message(config.groupid, 'Заявка от ' + name + ' (' + name1 + ') ' + '\n'
                         + f'Имя/(или никнейм) - {user.name} \n'
                         + f'Возраст  -  {user.will_learn} \n'
                         + f'Номер:  -  {user.languages} \n'
                         + f'Позвонить  -  {user.want_admin}'
                         + f'ID человека = {user_chats}', reply_markup=markup)
        # Проверка
    except Exception as e:
        bot.reply_to(message, '12!')


# При нажати на Телефон или Высказать предложение или жалобу /report
@bot.message_handler(commands=['report'])
def report_message(message):
    msg = bot.send_message(message.from_user.id, 'Опишите вашу проблем')
    bot.register_next_step_handler(msg, report_to_group)


def report_to_group(message):
    report = message.text
    user_name = message.from_user.username
    user_nick = message.from_user.first_name

    bot.send_message(message.from_user.id, 'Ваше сообщение доставлено, администрации рассмотрит вашу проблему')
    bot.send_message(config.groupid, user_name + '(' + user_nick + ')' + 'Отправил репорт: ' + report)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Анонимно')
    item2 = types.KeyboardButton('☎Оставить номер')
    item3 = types.KeyboardButton('/help')

    markup.add(item1, item2, item3)

    bot.send_message(message.chat.id, 'Добрый день, {0.first_name}!\n'
                                      'Наше руководство открыто к \n'
                                      'диалогу и хочет слышать \n'
                                      'мнение каждого сотрудника!\n'
                                      'Этот бот дает возможность \n'
                                      'сообщить руководству любую \n'
                                      'волнующую вас информацию о \n'
                                      'работе Компании, высказать \n'
                                      'предложение или пожелание, \n'
                                      'запросить необходимые документы, или задать \n'
                                      'вопрос!'.format(message.from_user), reply_markup=markup)

    bot.send_message(message.chat.id, 'Выберите вариант \n'
                                      'общения с ботом \n'
                                      'ниже:'.format(message.from_user), reply_markup=markup)


@bot.message_handler(content_types=['text'])
def bot_massage(message):
    if message.chat.type == 'private':
        if message.text == '/help':
            bot.send_message(message.chat.id, 'Привет, я бот сообщества от компании ****, \n'
                                              'если хочешь зарегистрироваться напиши /tell, \n'
                                              'рассказать о проблеме /report')
        elif message.text == 'Анонимно':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Высказать предложение или жалобу')
            item2 = types.KeyboardButton('Запросить стандартные кадровые шаблоны')
            item3 = types.KeyboardButton('Сказать спасибо коллегам другого подразделения')
            back = types.KeyboardButton('Назад')
            markup.add(item1, item2, item3, back)

            bot.send_message(message.chat.id, 'Анонимно', reply_markup=markup)
            bot.send_message(message.chat.id, 'На нашли нужную \nтему? \nНапишите сообщение ..')

        elif message.text == '☎Оставить номер':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Высказать предложение или жалобу')
            item2 = types.KeyboardButton('Запросить стандартные кадровые шаблоны')
            item3 = types.KeyboardButton('Сказать спасибо коллегам другого подразделения')
            back = types.KeyboardButton('Назад')
            markup.add(item1, item2, item3, back)

            bot.send_message(message.chat.id, '☎Оставить номер', reply_markup=markup)
            bot.send_message(message.chat.id, 'Напишите или нажмите на: /tell')

        elif message.text == 'Высказать предложение или жалобу':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Назад')
            markup.add(back)

            bot.send_message(message.chat.id, 'Уважаемый коллега! \n'
                                              'В поле ниже максимально \n'
                                              'открыто опишите ваше \n'
                                              'предложение или сообщите \n'
                                              'любую волнующую вас \n'
                                              'информацию о работе Компани. \n'
                                              'Напишите или нажмите на: /report \n')



        elif message.text == 'Запросить стандартные кадровые шаблоны':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Узнать количество дней отпуска ')
            item2 = types.KeyboardButton('Запросить обходной лист')
            item3 = types.KeyboardButton('Обратный звонок \nсотрудника отдела кадров')
            back = types.KeyboardButton('Назад')
            markup.add(item1, item2, item3, back)

            markup = types.InlineKeyboardMarkup()
            btn_my_site = types.InlineKeyboardButton(text='Заявление на отпуск без сохранения зп',
                                                     url='https://advdnr.ru/otpusk_bez_oplaty_2021.docx')
            markup.add(btn_my_site)
            bot.send_message(message.chat.id, 'Шаблон на отпуск без оплаты', reply_markup=markup)

            markup = types.InlineKeyboardMarkup()
            btn_my_site = types.InlineKeyboardButton(text='Заявление на ежегодный отпуск',
                                                     url='https://advdnr.ru/shablon_na_otpusk_2021.docx')
            markup.add(btn_my_site)
            bot.send_message(message.chat.id, 'Шаблон на отпуск', reply_markup=markup)

            markup = types.InlineKeyboardMarkup()
            btn_my_site = types.InlineKeyboardButton(text='Заявление на увольнение',
                                                     url='https://advdnr.ru/shablon_na_uvolnenie.doc')
            markup.add(btn_my_site)
            bot.send_message(message.chat.id, 'Шаблон на увольнение', reply_markup=markup)

        elif message.text == 'Сказать спасибо коллегам другого подразделения':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('😄ДА')
            item2 = types.KeyboardButton('😔НЕТ ')
            back = types.KeyboardButton('Назад')
            markup.add(item1, item2, back)

            bot.send_message(message.chat.id, 'Сказать спасибо коллегам другого подразделения', reply_markup=markup)
            bot.send_message(message.chat.id, 'Коллега! Мы благодарны за уделенное время!',
                             reply_markup=markup)
            bot.send_message(message.chat.id, 'Надеемся, Вам было полезно!',
                             reply_markup=markup)

        elif message.text == 'Назад':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Анонимно')
            item2 = types.KeyboardButton('☎Оставить номер')

            markup.add(item1, item2, )
            bot.send_message(message.chat.id, 'Назад', reply_markup=markup)


@server.route('/' + config.tokenbot, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_messages([update])
    return '!', 200


@server.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    return '!', 200


if __name__ == '__main__':
    server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
