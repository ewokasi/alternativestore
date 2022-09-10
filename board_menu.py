import datetime

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMedia
import clients_controller
import catalog_controller
from catalog_controller import get_makers, get_products

tastes_kw = {}


# All presets for the main menu keyboard
def markup_preset(call, bot):
    call_kw = {'mainmenu': "mainmenu", 'settings': "settings",
               'call_admin': "call_admin",
               'catalog': "catalog",
               'cart': "cart"
               }
    makers_kw = {}
    print(call.data)
    photo = None
    q = 1
    # Необходимый цикл чтобы добавить callback`и для динамической сборки кнопок меню
    for key in get_makers():
        makers_kw[f'{str("maker") + str(q)}'] = key
        call_kw[f'{str("maker") + str(q)}'] = key
        q = q + 1
    # Отписка, если пришел неизвестный callback
    keyboard = InlineKeyboardMarkup(row_width=2)
    text = "Что-то пошло не так, напиши /start"

    # Огромное ветвление, в котором написаны все пресеты. По выходе из оператора в bot.message_edit подставляются
    # объекты клавиатуры и заготовленный текст
    if call.data == call_kw['mainmenu']:

        catalog_btn = InlineKeyboardButton(text="Каталог 📋", callback_data="catalog")
        cart_btn = InlineKeyboardButton(text="Корзина 🛒", callback_data="cart")
        call_btn = InlineKeyboardButton(text="Связаться с админом 👷‍", callback_data="call_admin")
        keyboard.add(catalog_btn, cart_btn, call_btn)
        text = "Главное меню, вся навигация в этом окне через кнопки"
        photo = open(f"photos/mm.jpg", "rb")


    elif call.data == call_kw['settings']:
        back_btn = InlineKeyboardButton(text="Назад ◀", callback_data="mainmenu")
        keyboard.add(back_btn)
        text = "Настройки ⚙"

    elif call.data == call_kw['catalog']:

        text = "Выбери производителя"
        # из базы данных берутся имена производителей и подставляются в кнопки
        makers = get_makers()
        for maker in makers:
            keyboard.add(InlineKeyboardButton(text=maker, callback_data=maker))

        back_btn = InlineKeyboardButton(text="Назад ◀", callback_data="mainmenu")
        keyboard.add(back_btn)
        photo = open(f"photos/mm.jpg", "rb")


    elif call.data == call_kw['call_admin']:
        text = "Напиши мне в телеграмм: @ewoksicilin"
        back_btn = InlineKeyboardButton(text="Назад ◀", callback_data="mainmenu")
        keyboard.add(back_btn)
        photo = open(f"photos/ewoksicilin.jpg", "rb")


    elif call.data in makers_kw.values():
        text = "Товары проиводителя в наличии:"
        products = get_products(call.data)
        count = 1

        for product in products:
            taste = f"{str(call.data) + ', ' + str(product)}"
            keyboard.add(InlineKeyboardButton(text=product, callback_data=taste))

            tastes_kw[f'taste{count}'] = taste
            count += 1

        back_btn = InlineKeyboardButton(text="Назад ◀", callback_data="catalog")
        keyboard.add(back_btn)
        photo = open(f"photos/{call.data}.jpg", "rb")

    elif call.data in tastes_kw.values():

        cb_product = call.data.split(sep=", ")
        info = catalog_controller.find_product(cb_product[0], cb_product[1])

        text = f"{info[0]} {info[1]}\nТяг: {info[2]}\nЦена: {info[3]}\nВ наличии: {info[4]}"
        back_btn = InlineKeyboardButton(text="Назад ◀", callback_data=f"{cb_product[0]}")
        add_to_cart = InlineKeyboardButton(text="В корзину 🛒", callback_data=f"to_cart {call.data}")
        keyboard.add(add_to_cart, back_btn)



    elif "to_cart" in call.data:
        text = "В корзине ✅"
        clients_controller.add_to_cart(call)

        back_btn = InlineKeyboardButton(text="Назад ◀", callback_data='catalog')
        cart_btn = InlineKeyboardButton(text="Ваша корзина", callback_data="cart")
        keyboard.add(back_btn, cart_btn)



    elif call.data == call_kw['cart']:
        text = "Ваша корзина: \n"
        products = clients_controller.get_cart(call)

        for i in range(len(products)):
            text = text + "-"+products[i]["maker"] + " " + products[i]["taste"] + "\n"

        book_btn = InlineKeyboardButton(text="Забронировать", callback_data="book")

        clear_btn = InlineKeyboardButton(text="Очистить корзину", callback_data="clear_cart")
        back_btn = InlineKeyboardButton(text="Назад ◀", callback_data='mainmenu')
        keyboard.add(clear_btn, back_btn)
        photo = open(f"photos/cart.jpg", "rb")

        if len(products) > 0:
            keyboard.add(book_btn)

    elif call.data == "clear_cart":
        clients_controller.clear_cart(call)
        text = "Ваша корзина: \n"
        back_btn = InlineKeyboardButton(text="Назад ◀", callback_data='mainmenu')
        keyboard.add(back_btn)

    elif call.data == "book":
        info = clients_controller.add_book(call)
        text = f"Ваш заказ оформлен\n"

        back_btn = InlineKeyboardButton(text="Назад ◀", callback_data='mainmenu')
        keyboard.add(back_btn)
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=text,
                              reply_markup=keyboard)

        keyboard_offer = InlineKeyboardMarkup()
        cancel = InlineKeyboardButton(text="Отменить заказ ❌", callback_data="cancel")
        keyboard_offer.add(cancel)

        bot.send_message(chat_id=call.message.chat.id, text=f"Номер заказа: #{info['key']}",
                         reply_markup=keyboard_offer)

        bot.send_message(chat_id=1931633887,
                         text=f"Новый заказ: #{info['key']}\nUsername @{info['username']}, {info['cart']}\n{info['chat_id']}")
        clients_controller.clear_cart(call)

        for i in range(len(info["cart"])):
            catalog_controller.catalog_sell(info["cart"][i]['maker'], info["cart"][i]['taste'])


    elif call.data == "cancel":
        cur_text = call.message.text

        print(call.message.text[15:len(call.message.text)])
        text = cur_text + "\n\nВы уверены? Это действие удалит заказ из базы данных и этого чата."
        yes_btn = InlineKeyboardButton(text="✅", callback_data="yes")
        no_btn = InlineKeyboardButton(text="❌", callback_data="no")
        keyboard.add(no_btn, yes_btn)



    elif call.data == "yes":
        cur_text = call.message.text
        key = str(cur_text)[15:20]
        info = clients_controller.cancel_book(key)

        for pos in info['cart']:
            catalog_controller.catalog_add(pos['maker'], pos['taste'], count=1, puffs=1200, price=1)

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)



    elif call.data == "no":
        text = call.message.text.replace("\n\nВы уверены? Это действие удалит заказ из базы данных и этого чата.", "",
                                         1)

        cancel = InlineKeyboardButton(text="Отменить заказ ❌", callback_data="cancel")
        keyboard.add(cancel)


    elif call.data == "close_admin":
        cur_text = call.message.text

        text = cur_text + "\n\nВы уверены? Это действие закроет заказ и удалит его из базы данных и этого чата."
        yes_btn = InlineKeyboardButton(text="✅", callback_data="yes_c")
        no_btn = InlineKeyboardButton(text="❌", callback_data="no_c")
        keyboard.add(no_btn, yes_btn)

    elif call.data == 'yes_c':
        cur_text = call.message.text
        key = cur_text.split(sep="\n")[1]
        print(key)
        clients_controller.cancel_book(key)

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        return 1

    elif call.data == "no_c":
        text = call.message.text.replace(
            "\n\nВы уверены? Это действие закроет заказ и удалит его из базы данных и этого чата.", "",
            1)

        close = InlineKeyboardButton(text="Закрыть заказ", callback_data="close_admin")
        keyboard.add(close)

    elif call.data == "cat_plus":
        text = call.message.text
        first_str = text.split(sep="\n")[0]
        maker = first_str.split(sep=", ")[0]
        taste = first_str.split(sep=", ")[1]
        product = catalog_controller.catalog_change_count(maker, taste, 1)
        text = f"{product['maker']}, {product['taste']}\nТяг: {product['puffs']}\nЦена: {product['price']}\nКол-во: {product['count']}"
        plus_btn = InlineKeyboardButton(text="+1", callback_data="cat_plus")
        minus_btn = InlineKeyboardButton(text="-1", callback_data="cat_minus")
        keyboard.add(plus_btn, minus_btn)

    elif call.data == "cat_minus":
        text = call.message.text
        first_str = text.split(sep="\n")[0]
        maker = first_str.split(sep=", ")[0]
        taste = first_str.split(sep=", ")[1]
        product = catalog_controller.catalog_change_count(maker, taste, -1)
        text = f"{product['maker']}, {product['taste']}\nТяг: {product['puffs']}\nЦена: {product['price']}\nКол-во: {product['count']}"
        plus_btn = InlineKeyboardButton(text="+1", callback_data="cat_plus")
        minus_btn = InlineKeyboardButton(text="-1", callback_data="cat_minus")
        keyboard.add(plus_btn, minus_btn)

    if photo != None:
         bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id,
                           media=InputMedia(type='photo', media=photo, caption=text), reply_markup= keyboard)
    else:
        try:
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=text, reply_markup=keyboard)
        except:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=keyboard)