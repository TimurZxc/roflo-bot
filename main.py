import asyncio
import logging
import sys
import datetime
import jwt
from aiogram import Bot, Dispatcher, html, F
from aiogram.types.web_app_info import WebAppInfo
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, MenuButton
from config import TOKEN
from aiogram.exceptions import TelegramBadRequest
import random
import json

# TOKEN = getenv("BOT_TOKEN")

secret_key = '5d9bb8552c298f16adf7a7eaea27c8109ce1692d2cac4daee483902cbb7e878c'

dp = Dispatcher()
bot = Bot(token=TOKEN)



@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    try:
        await message.answer(f"Глаз Альнура")
    except TelegramBadRequest:
        print('Trigger form group')

# @dp.message(CommandStart())
# async def command_start_handler(message: Message) -> None:
#     payload = {
#         'tg_user_id': message.from_user.id,
#         'tg_username': message.from_user.username,
#         'exp': str(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)) 
#     }
#     jwt_token = jwt.encode(payload, secret_key, algorithm='HS256')
#     markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Launch Datester', web_app=WebAppInfo(url="https://datester-front.vercel.app/"))]])
#     try:
#         await message.answer(f"ALNUR KUPBAYEV!", reply_markup=markup)
#     except TelegramBadRequest:
#         print('Trigger form group')

@dp.message(Command('basement'))
async def basement_handler(message: Message) -> None:
    with open("database.json", "r") as f:
        data = json.load(f)
    await message.answer(f"Детей в подвале: {data.get('children', -1)}")

@dp.message(F.from_user.username == "awertkx")
async def alnur_message_handler(message: Message):
    children_addition = random.randint(1, 10)
    with open("database.json", "r") as f:
        data = json.load(f)
    children = data.get('children', -1) + children_addition
    data["children"] = children
    with open("database.json", "w") as f:
        json.dump(data, f, indent=4)
    await message.answer(f"Количество детей в подвале пополнено на {children_addition}")  


@dp.message(F.text == '#МыХотимТрахнутьАльнура!')
async def trah_message_handler(message: Message):
    with open("database.json", "r") as f:
        data = json.load(f)
    data['trah'] = True
    with open("database.json", "w") as f:
        json.dump(data, f, indent=4)
@dp.message(F.text == '#МожешьОтдохнутьАльнур')
async def trah_end_message_handler(message: Message):
    with open("database.json", "r") as f:
        data = json.load(f)
    data['trah'] = False
    with open("database.json", "w") as f:
        json.dump(data, f, indent=4)

@dp.message(Command('help'))
async def help_handler(message: Message) -> None:
    try:
        await message.answer("ПАШОЛ НАУХЙ")
    except:
        print('Help exception')

@dp.message(Command('get_me'))
async def get_me_handler(message: Message) -> None:
    await message.answer(str(message.from_user))


# @dp.message(F.text == 'сам такой')
# async def text_handler(message: Message) -> None:
#     await message.answer("((")


@dp.message()
async def echo_handler(message: Message) -> None:
    with open("database.json", "r") as f:
        data = json.load(f)
    if data.get('trah', False):
        response = await message.answer("#МыХотимТрахнутьАльнура!")
        await asyncio.sleep(60)
    
        await bot.delete_message(chat_id=response.chat.id, message_id=response.message_id)
    # try:
    #     await message.send_copy(chat_id=message.chat.id)
    # except TypeError:
    #     await message.answer("Nice try!")

async def main() -> None:
    await dp.start_polling(bot)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout) # ONLY FOR DEBUG
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')