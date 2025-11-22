from aiogram import Router, F
from aiogram.types import Message
from keyboards.keyboards import create_keys
from lexicon.lexicon import MAIN_MENU
from promt.create_db import delete_messages_by_chat_id
from promt.create_promt import generate_response_for_chat

dialog_router: Router = Router()
keyboard_start = create_keys(1, **MAIN_MENU)


@dialog_router.message(F.text == MAIN_MENU['menu_start'])
async def start_dialog(message: Message):
    delete_messages_by_chat_id(message.chat.id)
    await message.answer('Чем могу быть полезен?')


@dialog_router.message(F.text)
async def build_dialog(message: Message):
    chat_id = message.chat.id
    user_text = message.text
    await message.answer(generate_response_for_chat(chat_id, user_text))
