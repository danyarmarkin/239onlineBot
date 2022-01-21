from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
from enum import Enum
import database
import ServerUI


class Event(Enum):
    REG = 1
    PASS = 2


class Task:
    users_have_solve = []
    users_have_question = []
    users_have_no_solve = []
    name = ""


root = None
f = open('token.txt', "r")
token = f.readline()
updater = Updater(token, use_context=True)

events = dict()
selected_task = dict()

users = database.UsersTable()
if not users.exists():
    users.create()
tasks = []


def add_task(task: Task):
    global tasks
    tasks.append(task)


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "239 Online bot.\n/help для спракви")


def help(update: Update, context: CallbackContext):
    user = users.getUser(update.message.from_user.id)
    update.message.reply_text(f"""
    Вы зарегестрированы как
    *{user[0]} {user[1]}*
    Команды
    /reg - зарегистрироваться
    /help - этот текст
    /task - выбрать задачу""", parse_mode="markdown")


def reg(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    events[user_id] = Event.PASS
    update.message.reply_text("Введите пароль")


def choose_task(update: Update, context: CallbackContext):
    global tasks

    button_list = []
    for task in tasks:
        button_list.append(InlineKeyboardButton(task.name, callback_data=task.name))
    markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=3))
    update.message.reply_text("выберите задачу", reply_markup=markup)


def callback(update: Update, context: CallbackContext):
    global tasks, selected_task, users, root

    query = update.callback_query
    data = query.data
    bot = context.bot

    tasks_names = [task.name for task in tasks]
    actions = ["Я сделал", "У меня не получается", "Вопрос по условию"]

    if data in actions:
        task_name = selected_task.get(query.from_user.id, None)
        task = None
        if task_name is None:
            return
        for t in tasks:
            if t.name == task_name:
                task = t
                break
        try:
            task.users_have_solve.remove(query.from_user.id)
        except ValueError:
            pass
        try:
            task.users_have_no_solve.remove(query.from_user.id)
        except ValueError:
            pass
        try:
            task.users_have_question.remove(query.from_user.id)
        except ValueError:
            pass

        if data == actions[0]:
            task.users_have_solve.append(query.from_user.id)
        elif data == actions[1]:
            task.users_have_no_solve.append(query.from_user.id)
        elif data == actions[2]:
            task.users_have_question.append(query.from_user.id)
        selected_task[query.from_user.id] = None

        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=f"В задаче *{task_name}* выбрано *{data}*",
            parse_mode="markdown"
        )
        query.answer()
        ServerUI.update(root, tasks, users)
        return

    if data not in tasks_names:
        query.answer()
        return

    selected_task[query.from_user.id] = data
    button_list = []
    for a in actions:
        button_list.append(InlineKeyboardButton(a, callback_data=a))
    markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))

    query.answer(f"Выбрана задача {data}")
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=f"выберите действие по задаче {data}",
        reply_markup=markup
    )


def text_analyze(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text
    print(f"{user_id} {update.message.from_user.full_name} (registered = {users.haveUser(user_id)}): {text}")
    try:
        event = events[user_id]
    except KeyError:
        event = None

    if event == Event.REG and len(text.split()) == 2:
        surname, name = tuple(text.split())
        users.add(user_id, name, surname)
        update.message.reply_text(f"Вы зарегистрировались как {surname} {name}")
    elif event == Event.PASS:
        f = open("password.txt", "r")
        if text == f.readline():
            events[user_id] = Event.REG
            update.message.reply_text("Введите Фамилию и Имя (Иванов Иван)")
            return
        else:
            update.message.reply_text("неверный пароль")
    else:
        update.message.reply_text("Что-то на эльфийском")
    events[user_id] = None


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('reg', reg))
updater.dispatcher.add_handler(CommandHandler('task', choose_task))
updater.dispatcher.add_handler(CallbackQueryHandler(callback))

updater.dispatcher.add_handler(MessageHandler(Filters.text, text_analyze))


def start_bot(r):
    global root
    root = r
    updater.start_polling()
