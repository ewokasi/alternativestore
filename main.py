# -*- coding: utf-8 -*-
# v 0.2 pre-release
import telebot
import catalog_controller
import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import clients_controller
from board_menu import markup_preset
from datetime import datetime

# Start settings
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)
Token = '5442133786:AAE-rRU7ZbFCkKbzvgazOEhdOoZ0tvd_CP4'
Beta_Token = '5626676453:AAHACc2r_UNmVKPP5w7b3naBTT-8aKmPTpE'
bot = telebot.TeleBot(Beta_Token)
# reading list of user with permissions
file = open(r"admins.txt")
admins = file.read().splitlines()
file.close()


# Greeting and tutorial
@bot.message_handler(commands=["start"])
def start_answer(message):
    # Recording visits from users
    with open(r"clients.txt", "a") as clients:
        clients.write(f"{message.chat.username} {message.chat.id} {datetime.today()} \n")

    # assembling the main menu keyboard
    keyboard = InlineKeyboardMarkup(row_width=2)
    catalog_btn = InlineKeyboardButton(text="Каталог 📋", callback_data="catalog")
    setings_btn = InlineKeyboardButton(text="Корзина 🛒", callback_data="cart")
    call_btn = InlineKeyboardButton(text="Связаться с админом 👷", callback_data="call_admin")
    keyboard.add(catalog_btn, setings_btn, call_btn)
    bot.send_message(message.chat.id, "Главное меню, вся навигация в этом окне через кнопки\n\nДля корректной работы бота проверьте, что у вас есть username, сделать вы это можете, нажав /username. В противном случае админ не сможет связаться с вами самостоятельно",
                     reply_markup=keyboard)


# ADMIN Adding a product via catalog_controller
@bot.message_handler(commands=["add"])
def add_to_catalog(message):
    # Test for admin username
    if message.chat.username not in admins:
        return 1

    entity = catalog_controller.separator(message.text, "/add")

    if entity != "":
        if entity['price'] != "":
            catalog_controller.catalog_add(entity['maker'], entity['taste'], entity['puffs'], entity['price'],
                                           entity['count'])
            bot.send_message(message.chat.id, f"Added {entity['maker'], entity['taste']}")
        else:
            catalog_controller.catalog_add(entity['name'], count=entity['count'])
            bot.send_message(message.chat.id, f"Added '{entity['name']}' without price")
    else:
        bot.send_message(message.chat.id, "Вы не указали товар для добавления")


# ADMIN Deleting a product via catalog_controller
@bot.message_handler(commands=['delete'])
def delete_product(message):
    if message.chat.username in admins:
        product = catalog_controller.separator(message.text, "/delete")
        deleted = catalog_controller.catalog_del(product['maker'], product['taste'])

        if product['maker'] == '':
            bot.send_message(message.chat.id, "Вы не указали продукт")
        else:
            if deleted == 0:
                bot.send_message(message.chat.id, "Not Found")
            else:
                bot.send_message(message.chat.id, f"Deleted {deleted}")


# ADMIN Selling a product via catalog_controller
@bot.message_handler(commands=["sell"])
def product_sell(message):
    if message.chat.username in admins:
        product = catalog_controller.separator(message.text, '/sell')
        sold = catalog_controller.catalog_sell(product['maker'], product['taste'], product['count'])
        if product['maker'] == '':
            bot.send_message(message.chat.id, "Вы не указали продукт")
        else:
            if sold == 0:
                bot.send_message(message.chat.id, "Not Found")
            else:
                bot.send_message(message.chat.id, f"Sold {sold}")


# ADMIN Removes last position via catalog_controller
@bot.message_handler(commands=["removepos"])
def remove_last_add(data):
    if data.chat.username not in admins: return 1
    catalog_controller.remove_last_pos()
    bot.send_message(data.chat.id, "Removed")


# Assembling menu with presets from board_menu
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    markup_preset(call, bot)


# ADMIN manual closing of active offer
@bot.message_handler(commands=["cancelkey"])
def cancel_book_by_key(message):
    if message.chat.username in admins:
        key = message.text.replace("/cancelkey ", "", 1)
        clients_controller.cancel_book(key)

        bot.send_message(message.chat.id, key + "canceled")


# Check for username
@bot.message_handler(commands=["username"])
def get_username(message):

    if message.chat.username == None or message.chat.username == 'null':
        bot.send_message(chat_id=message.chat.id,
                         text=f"Ваше имя пользователя '{message.chat.username}' не указано, Укажите его в настройках ❌")
    else:
        bot.send_message(chat_id=message.chat.id,
                         text=f"Ваше имя пользователя '{message.chat.username}'. Все отлично 🆗")


# ADMIN Show all active offers
@bot.message_handler(commands=["showbooks"])
def show_books(message):
    if message.chat.username in admins:
        books = clients_controller.get_books()
        for book in books:
            keyboard = InlineKeyboardMarkup()
            close_btn = InlineKeyboardButton(text="Закрыть заказ", callback_data="close_admin")
            keyboard.add(close_btn)

            bot.send_message(message.chat.id, book, reply_markup=keyboard)
        bot.send_message(message.chat.id, f'Всего активных заказов {len(books)}')


# ADMIN send the copy of current catalog
@bot.message_handler(commands=["catalog"])
def show_catalog(message):
    if message.chat.username in admins:
        catalog = catalog_controller.catalog_get()
        keyboard = InlineKeyboardMarkup(row_width= 3)

        plus_btn = InlineKeyboardButton(text="+1", callback_data="cat_plus")
        minus_btn = InlineKeyboardButton(text="-1", callback_data="cat_minus")
        keyboard.add( plus_btn,minus_btn)
        for product in catalog:
            bot.send_message(message.chat.id, text=f"{product['maker']}, {product['taste']}\nТяг: {product['puffs']}\nЦена: {product['price']}\nКол-во: {product['count']}",
                             reply_markup= keyboard)


# ADMIN help menu
@bot.message_handler(commands=["adminhelp"])
def admin_help(message):
    if message.chat.username in admins:
        text = "Список команд администратора\n\n" \
               "/add HQD, Мох, 1200, 599, 1 - добавляет продукт в каталог, если продукт новый, добавляется в конец\n\n" \
               "/delete HQD, Мох - удаляет проудкт из каталога\n\n" \
               "/sell HQD, Мох - изменяет количесвто в налии в каталоге\n\n" \
               "/removepos - удаляет последний продукт в каталоге\n\n" \
               "/cancelkey E-710 - позволяет вручную удалить заказ\n\n" \
               "/showbooks - показывает список всех активных заказов, также можно удалить заказ через кнопки\n\n" \
               "/start - вызов главного меню"

        bot.send_message(message.chat.id, text=text)


# Infinity polling for bot
if __name__ == "__main__":

    while 1:
        try:
            bot.infinity_polling()
        except Exception:
            continue

