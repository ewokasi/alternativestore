import json
from random import randint


def add_to_cart(call):
    username = call.message.chat.username
    chat_id = call.message.chat.id
    call.data = call.data.replace("to_cart ", "", 1)

    with open("clients.json", 'r') as file:
        db = json.load(file)
        clients = db['clients']

    maker = call.data.split(sep=", ")[0]
    taste = call.data.split(sep=", ")[1]

    offer = {
        "username": username,
        "chat_id": chat_id,
        "cart": [
            {
                "maker": maker,
                "taste": taste
            }
        ]

    }

    # Если заказ первый, и если второй
    is_found = 0
    for client in clients:
        if offer["chat_id"] == client["chat_id"]:
            client["cart"].append(offer["cart"][0])
            db["clients"] = clients
            with open("clients.json", 'w') as file:
                json.dump(db, file, indent=2)

            is_found = 1
            break

    if is_found == 0:
        clients.append(offer)
        db["clients"] = clients
        with open("clients.json", 'w') as file:
            json.dump(db, file, indent=2)

    return offer


def clear_cart(call):
    username = call.message.chat.username
    chat_id = call.message.chat.id

    with open("clients.json", 'r') as file:
        db = json.load(file)
        clients = db['clients']

    for client in clients:
        if client["chat_id"] == chat_id:
            client["cart"] = []
            db["clients"] = clients
            with open("clients.json", 'w') as file:
                json.dump(db, file, indent=2)
            break


def get_cart(call):
    username = call.message.chat.username
    chat_id = call.message.chat.id

    with open("clients.json", 'r') as file:
        db = json.load(file)
        clients = db['clients']

    for client in clients:
        if chat_id == client["chat_id"]:
            return client['cart']


def add_book(call):
    # сделать бронь товара - перенести карт юзера из клинт в букс
    username = call.message.chat.username
    chat_id = call.message.chat.id

    with open("books.json", 'r') as file:
        books_db = json.load(file)

    with open("clients.json", 'r') as file:
        clients_db = json.load(file)
        clients = clients_db["clients"]

    for client in clients:
        if chat_id == client["chat_id"]:
            cart = client["cart"]
            break

    client = {
        "username": username,
        "chat_id": chat_id,
        "key": str(username[0].upper()) + "-" + str(randint(100, 999)),
        "cart": cart
    }

    with open("books.json", "w") as file:
        books_db["books"].append(client)
        json.dump(books_db, file, indent=2)

    return client


def cancel_book(key):
    with open("books.json", 'r') as file:
        db = json.load(file)
        books = db['books']

    for book in books:
        if key == book['key']:
            deleted = book
            books.remove(book)
            db["books"] = books
            with open("books.json", 'w') as file:
                json.dump(db, file, indent=2)

            return deleted


def get_books():
    with open("books.json", 'r') as file:
        db = json.load(file)
        books = db['books']

    output = []
    for book in books:
        key = str(book['key'])
        username = "@" + str(book["username"])
        cart = str(book['cart'])
        data = username + "\n" + key + "\n" + cart + "\n"

        output.append(data)

    return output

#if __name__ == "__main__":
    # print(cancel_book("E-621"))