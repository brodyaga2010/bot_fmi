import telebot
from telebot import types
import logging
import datetime
import json
import os
import configparser
from enum import Enum
import time


class State(Enum):
    MAIN_MENU = 1
    ABOUT_PROGRAMS = 2
    HOW_TO_APPLY = 3
    ADMISSION = 4
    STUDENT_LIF = 5
    MORE_QUESTIONS = 6
    TO_TALK = 7
    POST = 8


def save_user_states(user_states):
    with open('user_states.json', 'w') as file:
        json.dump(user_states, file)


def load_user_states():
    try:
        with open('user_states.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


# Устанавливаем уровень логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

file_handler = logging.FileHandler('bot_log.log', encoding="UTF-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger.addHandler(file_handler)

admins = {'432739846'}
user_state = load_user_states()  # словарь для хранения состояния каждого пользователя
print(user_state)

config = configparser.ConfigParser()
config.read("bot_config.ini")
token = config.get('Bot', 'token')

# Загрузка словаря из JSON-файла
with open('text_information.json', 'r', encoding="UTF-8") as f:
    info_text = json.load(f)

bot = telebot.TeleBot(token)

keyboard_main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_main_menu.row("Об учебных программах", "Как поступить")
keyboard_main_menu.row("Приёмная комиссия", "Студенческие будни")
keyboard_main_menu.row("Ещё вопросы?", "А поговорить...")

keyboard_about_programs = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_about_programs.row("Направления обучения", "Сколько бюджетных мест")
keyboard_about_programs.row("Даты подачи документов", "Предметы для поступления")
keyboard_about_programs.row("Назад")

keyboard_how_to_apply = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_how_to_apply.row("Какие документы и как подать", "Сколько можно выбрать направлений")
keyboard_how_to_apply.row("Как поступить после колледжа", "Победители и Призеры Олимпиад")
keyboard_how_to_apply.row("Назад")

keyboard_admission = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_admission.row("Время работы приемной комиссии", "Скорость обработки заявления")
keyboard_admission.row("Назад")

keyboard_student_life = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_student_life.row("Какая стипендия?", "Общежития. Где находятся?")
keyboard_student_life.row("А что со спортом?", "Чем еще можно заняться?")
keyboard_student_life.row("Назад")

keyboard_back = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_back.row("Назад")


@bot.message_handler(commands=['start'])
def main_menu(message):
    user_state[str(message.chat.id)] = State.MAIN_MENU.value
    user = message.chat
    bot.send_message(user.id,
                     f"Привет, {user.first_name}!\n"
                     f"Я бот-помощник Физико-математического института - Фима!\nЧто тебя интересует?",
                     reply_markup=keyboard_main_menu)
    logger.info(f"{user.id} : {message.text}")
    log_user_action(user.id, f"{user.id} : {message.text}")
    save_user_states(user_state)


@bot.message_handler(func=lambda message: user_state.get(
    str(message.chat.id)) == State.MAIN_MENU.value and message.text == 'Об учебных программах')
def about_programs_submenu(message):
    user_state[str(message.chat.id)] = State.ABOUT_PROGRAMS.value
    user = message.chat
    bot.send_message(user.id, "Тут информация об учебных программах\nВыбери, что тебя интересует:",
                     reply_markup=keyboard_about_programs)
    logger.info(f"{user.id} : {message.text}")
    log_user_action(user.id, f"{user.id} : {message.text}")
    save_user_states(user_state)


@bot.message_handler(func=lambda message: user_state.get(str(message.chat.id)) == State.ABOUT_PROGRAMS.value)
def handle_about_programs(message):
    user_text = message.text
    user = message.chat
    menu = ["Направления обучения", "Сколько бюджетных мест", "Даты подачи документов", "Предметы для поступления"]
    if user_text in menu:
        bot.send_message(user.id, info_text[user_text], parse_mode="HTML")
    elif user_text == "Назад":
        user_state[str(message.chat.id)] = State.MAIN_MENU.value
        bot.send_message(user.id, "Что тебя интересует:", reply_markup=keyboard_main_menu)
    else:
        bot.send_message(user.id, "Пожалуйста, выберите пункт меню.")
    logger.info(f"{user.id} : {user_text}")
    log_user_action(user.id, f"{user.id} : {user_text}")
    save_user_states(user_state)


# Обработчик подменю "Как поступить"
@bot.message_handler(func=lambda message: user_state.get(
    str(message.chat.id)) == State.MAIN_MENU.value and message.text == 'Как поступить')
def how_to_apply_submenu(message):
    user_state[str(message.chat.id)] = State.HOW_TO_APPLY.value
    user = message.chat
    bot.send_message(user.id, "Тут информация о поступлении\nВыбери, что тебя интересует:",
                     reply_markup=keyboard_how_to_apply)
    logger.info(f"{user.id} : {message.text}")
    log_user_action(user.id, f"{user.id} : {message.text}")
    save_user_states(user_state)


@bot.message_handler(func=lambda message: user_state.get(str(message.chat.id)) == State.HOW_TO_APPLY.value)
def handle_how_to_apply(message):
    user_text = message.text
    user = message.chat
    menu = ["Какие документы и как подать", "Сколько можно выбрать направлений", "Как поступить после колледжа",
            "Победители и Призеры Олимпиад"]
    if user_text in menu:
        bot.send_message(user.id, info_text[user_text], parse_mode="HTML")
    elif user_text == "Назад":
        user_state[str(message.chat.id)] = State.MAIN_MENU.value
        bot.send_message(user.id, "Что тебя интересует:", reply_markup=keyboard_main_menu)
    else:
        bot.send_message(user.id, "Пожалуйста, выберите пункт меню.")
    logger.info(f"{user.id} : {user_text}")
    log_user_action(user.id, f"{user.id} : {user_text}")
    save_user_states(user_state)


# Обработчик подменю "Приёмная комиссия"
@bot.message_handler(func=lambda message: user_state.get(
    str(message.chat.id)) == State.MAIN_MENU.value and message.text == 'Приёмная комиссия')
def admission_submenu(message):
    user_state[str(message.chat.id)] = State.ADMISSION.value
    user = message.chat
    bot.send_message(user.id, "Тут информация о приёмной комиссии\nВыбери, что тебя интересует:",
                     reply_markup=keyboard_admission)
    logger.info(f"{user.id} : {message.text}")
    log_user_action(user.id, f"{user.id} : {message.text}")
    save_user_states(user_state)


@bot.message_handler(func=lambda message: user_state.get(str(message.chat.id)) == State.ADMISSION.value)
def handle_admission(message):
    user_text = message.text
    user = message.chat
    menu = ["Время работы приемной комиссии", "Скорость обработки заявления"]
    if user_text in menu:
        bot.send_message(user.id, info_text[user_text], parse_mode="HTML")
    elif user_text == "Назад":
        user_state[str(message.chat.id)] = State.MAIN_MENU.value
        bot.send_message(user.id, "Что тебя интересует:", reply_markup=keyboard_main_menu)
    else:
        bot.send_message(user.id, "Пожалуйста, выберите пункт меню.")
    logger.info(f"{user.id} : {user_text}")
    log_user_action(user.id, f"{user.id} : {user_text}")
    save_user_states(user_state)


# Обработчик подменю "Студенческие будни"
@bot.message_handler(func=lambda message: user_state.get(
    str(message.chat.id)) == State.MAIN_MENU.value and message.text == 'Студенческие будни')
def student_life_submenu(message):
    user_state[str(message.chat.id)] = State.STUDENT_LIF.value
    user = message.chat
    bot.send_message(user.id, "Тут информация о студенческой жизни\nВыбери, что тебя интересует:",
                     reply_markup=keyboard_student_life)
    logger.info(f"{user.id} : {message.text}")
    log_user_action(user.id, f"{user.id} : {message.text}")
    save_user_states(user_state)


@bot.message_handler(func=lambda message: user_state.get(str(message.chat.id)) == State.STUDENT_LIF.value)
def handle_student_life(message):
    user_text = message.text
    user = message.chat
    menu = ["Какая стипендия?", "Общежития. Где находятся?", "А что со спортом?", "Чем еще можно заняться?"]
    if user_text in menu:
        bot.send_message(user.id, info_text[user_text], parse_mode="HTML")
    elif user_text == "Назад":
        user_state[str(message.chat.id)] = State.MAIN_MENU.value
        bot.send_message(user.id, "Что тебя интересует:", reply_markup=keyboard_main_menu)
    else:
        bot.send_message(user.id, "Пожалуйста, выберите пункт меню.")
    logger.info(f"{user.id} : {user_text}")
    log_user_action(user.id, f"{user.id} : {user_text}")
    save_user_states(user_state)


# Обработчик подменю "Ещё вопросы?"
@bot.message_handler(func=lambda message: user_state.get(
    str(message.chat.id)) == State.MAIN_MENU.value and message.text == 'Ещё вопросы?')
def more_questions_submenu(message):
    user_state[str(message.chat.id)] = State.MORE_QUESTIONS.value
    user = message.chat
    bot.send_message(user.id, info_text[message.text], parse_mode="HTML", reply_markup=keyboard_back)
    logger.info(f"{user.id} : {message.text}")
    log_user_action(user.id, f"{user.id} : {message.text}")
    save_user_states(user_state)


@bot.message_handler(func=lambda message: user_state.get(str(message.chat.id)) == State.MORE_QUESTIONS.value)
def handle_more_questions(message):
    user_text = message.text
    user = message.chat
    if user_text == "Назад":
        user_state[str(message.chat.id)] = State.MAIN_MENU.value
        bot.send_message(user.id, "Что тебя интересует:", reply_markup=keyboard_main_menu)
    else:
        # Сохраняем вопрос абитуриента в текстовый файл
        with open("questions.txt", "a", encoding="UTF-8") as file:
            question = f"Вопрос от {message.from_user.username} (id:{message.from_user.id}): {user_text}\n"
            file.write(question)
        for admin_id in admins:
            bot.send_message(admin_id, question)
        logger.info(question[:-1])
        # Отправляем сообщение о том, что вопрос был передан на обработку
        bot.reply_to(message, "Ваш вопрос был передан на обработку. Мы постараемся ответить в ближайшее время.")
    logger.info(f"{user.id} : {user_text}")
    log_user_action(user.id, f"{user.id} : {user_text}")
    save_user_states(user_state)


# Обработчик подменю "А поговорить..."
@bot.message_handler(func=lambda message: user_state.get(
    str(message.chat.id)) == State.MAIN_MENU.value and message.text == 'А поговорить...')
def to_talk_submenu(message):
    user_state[str(message.chat.id)] = State.TO_TALK.value
    user = message.chat
    bot.send_message(user.id,
                     "Здесь скоро появится Наш искуственный интелект ФИМА, а пока предлагаем изучить другие блоки =)",
                     reply_markup=keyboard_back)
    logger.info(f"{user.id} : {message.text}")
    log_user_action(user.id, f"{user.id} : {message.text}")
    save_user_states(user_state)


@bot.message_handler(func=lambda message: user_state.get(str(message.chat.id)) == State.TO_TALK.value)
def handle_to_talk(message):
    user_text = message.text
    user = message.chat
    if user_text == "Назад":
        user_state[str(message.chat.id)] = State.MAIN_MENU.value
        bot.send_message(user.id, "Что тебя интересует:", reply_markup=keyboard_main_menu)
    else:
        bot.send_message(user.id, message.text)
    logger.info(f"{user.id} : {user_text}")
    log_user_action(user.id, f"{user.id} : {user_text}")
    save_user_states(user_state)


@bot.message_handler(commands=['reply'])
def reply_more_questions(message):
    # Проверяем, является ли пользователь администратором
    if str(message.from_user.id) not in admins:
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return

    # Получаем аргументы команды
    args = message.text.split()[1:]
    if len(args) < 2:
        bot.reply_to(message, "Используйте команду следующим образом: /reply <user_id> <сообщение>")
        return

    # Получаем id пользователя и текст сообщения
    user_id = args[0]
    message_text = ' '.join(args[1:])

    try:
        # Отправляем сообщение пользователю
        bot.send_message(user_id, f'Ответ на твой вопрос:\n{message_text}')
        bot.reply_to(message, "Сообщение успешно отправлено.")
    except Exception as err:
        bot.reply_to(message, f"Не удалось отправить сообщение: {str(err)}")
    logger.info(f"{message.chat.id} : {message_text}")
    log_user_action(message.chat.id, f"{message.chat.id} : {message_text}")


@bot.message_handler(commands=['post'])
def post(message):
    user = message.chat.id
    if str(user) in admins:
        user_state[str(user)] = State.POST.value  # устанавливаем состояние POST
        bot.send_message(user, "Введите сообщение для отправки:", reply_markup=keyboard_back)
    else:
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
    logger.info(f"{user} : post")
    log_user_action(message.chat.id, f"{user} : post")


@bot.message_handler(func=lambda message: user_state.get(str(message.chat.id)) == State.POST.value)
def handle_message_for_broadcast(message):
    user_text = message.text
    user = message.chat
    if user_text == 'Назад':
        user_state[str(user.id)] = State.MAIN_MENU.value
        bot.send_message(user.id, "Что тебя интересует:", reply_markup=keyboard_main_menu)
        save_user_states(user_state)
    else:
        users = list_students()
        for user_id in users:
            bot.send_message(user_id, user_text)
        bot.reply_to(message, "Рассылка завершена.")
    logger.info(f"{user.id} : {user_text}")
    log_user_action(user.id, f"{user.id} : {user_text}")


@bot.message_handler(func=lambda message: user_state.get(str(message.chat.id)) != State.TO_TALK.value)
def handle_to_talk(message):
    user_text = message.text
    user = message.chat
    if user_text == "Назад":
        user_state[str(message.chat.id)] = State.MAIN_MENU.value
        bot.send_message(user.id, "Что тебя интересует:", reply_markup=keyboard_main_menu)
    else:
        bot.send_message(user.id, message.text)
    logger.info(f"{user.id} : {user_text}")
    log_user_action(user.id, f"{user.id} : {user_text}")
    save_user_states(user_state)


def list_students():
    folder_path = "user_logs"
    file_list = os.listdir(folder_path)
    id_list = [os.path.splitext(file)[0] for file in file_list]
    return id_list


def log_user_action(user_id, action):
    time_data = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file_path = f'user_logs/{user_id}.txt'
    with open(log_file_path, 'a', encoding="UTF-8") as file:
        file.write(f'{time_data} : {action}\n')


while True:
    try:
        bot.polling()

    except telebot.apihelper.ApiException as error:
        if error.result.status_code == 429:
            sleep_time = error.result.json()['parameters']['retry_after']
            print(f"Too many requests! Sleeping for {sleep_time} seconds")
            time.sleep(sleep_time)
        else:
            raise error
    except KeyboardInterrupt:
        print("Bot stopped by user")
        break
