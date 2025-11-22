from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def create_keys(wight: int, *args: str, **kwargs: str):
    menu: ReplyKeyboardBuilder = ReplyKeyboardBuilder()

    buttons: list[KeyboardButton] = []

    if args:
        for button in args:
            buttons.append(KeyboardButton(text=button))

    if kwargs:
        for key, value in kwargs.items():
            buttons.append(KeyboardButton(text=value, resize_keyboard=True))

    menu.row(*buttons, width=wight)
    return menu.as_markup()
