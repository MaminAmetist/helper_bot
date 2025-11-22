from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from keyboards.keyboards import create_keys
from lexicon.lexicon import MAIN_MENU
from promt.create_db import delete_messages_by_chat_id

start_router: Router = Router()
keyboard_start = create_keys(1, **MAIN_MENU)


@start_router.message(CommandStart())
async def start_bot(message: Message):
    delete_messages_by_chat_id(message.chat.id)
    await message.answer(f'Приветствую тебя, {message.from_user.full_name}.\n'
                         f'Для начала диалога нажми кнопку {MAIN_MENU["menu_start"]}.\n'
                         f'Если тебе нужна помощь вызови команду /help.\n',
                         reply_markup=keyboard_start)


@start_router.message(Command("help"))
async def help_bot(message: Message):
    await message.answer(f'Не паникуй, {message.from_user.full_name}, помощь уже в пути.')
