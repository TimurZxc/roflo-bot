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
COOLDOWN_FILE = "user_cooldowns.json"
DATABASE_FILE = "database.json"
COOLDOWN_PERIOD = datetime.timedelta(hours=1)
dp = Dispatcher()
bot = Bot(token=TOKEN)
def load_cooldowns():
    try:
        with open(COOLDOWN_FILE, "r") as f:
            return {int(k): datetime.datetime.fromisoformat(v) for k, v in json.load(f).items()}
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

# Save cooldown data to JSON file
def save_cooldowns(cooldowns):
    with open(COOLDOWN_FILE, "w") as f:
        json.dump({k: v.isoformat() for k, v in cooldowns.items()}, f, indent=4)

def load_databese():
    try:
        with open(DATABASE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}
    
def save_database(data):
    with open(DATABASE_FILE, "w") as f:
        json.dump(data, f, indent=4)

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
    data = load_databese()
    await message.answer(f"Детей в подвале: {data.get('children', -1)}")

@dp.message(F.from_user.username == "awertkx")
async def alnur_message_handler(message: Message):
    children_addition = random.randint(1, 10)
    data = load_databese()

    children = data.get('children', -1) + children_addition
    data["children"] = children
    save_database(data)
    await message.answer(f"Количество детей в подвале пополнено на {children_addition}")  


@dp.message(F.text == '#МыХотимТрахнутьАльнура!')
async def trah_message_handler(message: Message):
    data = load_databese()
    
    data['trah'] = True
    save_database(data)

@dp.message(F.text == '#МожешьОтдохнутьАльнур')
async def trah_end_message_handler(message: Message):
    data = load_databese()

    data['trah'] = False
    save_database(data)
    

@dp.message(Command('help'))
async def help_handler(message: Message) -> None:
    try:
        await message.answer("ПАШОЛ НАУХЙ")
    except:
        print('Help exception')

@dp.message(Command('get_me'))
async def get_me_handler(message: Message) -> None:
    await message.answer(str(message.from_user))

@dp.message(Command('save_children'))
async def save_children_handler(message: Message) -> None:
    save_number = random.randint(1, 6)
    data = load_databese()

    data['save_number'] = save_number
    save_database(data)
    
    await message.answer(f"Чтобы спасти детей выбейте {save_number} на кубике!")

@dp.message(F.dice)
async def dice_handler(message: Message) -> None:
    current_time = datetime.datetime.now(datetime.timezone.utc)
    user_cooldowns = load_cooldowns()   
    last_roll_time = user_cooldowns.get(message.from_user.id)
    if last_roll_time and current_time < last_roll_time + COOLDOWN_PERIOD:
        await message.answer("Подожди час перед тем, как снова бросить кубик!")
        return
    
    user_cooldowns[message.from_user.id] = current_time
    
    save_cooldowns(user_cooldowns)
    data = load_databese()
    if message.dice.value == data.get('save_number', -1):
        data["children"] = 0
        save_database(data)
        if message.from_user.username == "awertkx":
            await message.answer("Ебать, Альнур решил отпустить своих заключенных, видимо сбор намечается.")
        else:
            await message.answer(f"Ахуеть, вы спасли детей! Похлопаем @{message.from_user.username}!")
    else:
        unluck_number = random.randint(10, 20)
        data["children"] = data["children"] + unluck_number
        save_database(data)
        await message.answer(f"Вы проиграли! Альнур узнал о ваших намериниях и словил еще {unluck_number} детей!")


@dp.message()
async def echo_handler(message: Message) -> None: 
    data = load_databese()
    if data.get('trah', False):
        response = await message.answer("#МыХотимТрахнутьАльнура!")
        await asyncio.sleep(60)
    
        await bot.delete_message(chat_id=response.chat.id, message_id=response.message_id)


async def main() -> None:
    await dp.start_polling(bot)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout) # ONLY FOR DEBUG
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')