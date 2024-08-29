import asyncio
import logging
import sys
import datetime
from aiogram import Bot, Dispatcher, html, F
from aiogram.types.web_app_info import WebAppInfo
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, MenuButton
from config import TOKEN
from aiogram.exceptions import TelegramBadRequest
import random
from utils import *
from rps import register_handlers_rps
from bot import bot

# TOKEN = getenv("BOT_TOKEN")

secret_key = '5d9bb8552c298f16adf7a7eaea27c8109ce1692d2cac4daee483902cbb7e878c'

dp = Dispatcher()
register_handlers_rps(dp)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    try:
        await message.answer(f"Глаз Альнура")
    except TelegramBadRequest:
        print('Trigger form group')


@dp.message(Command('basement'))
async def basement_handler(message: Message) -> None:
    data = load_database()
    await message.answer(f"Детей в подвале: {data.get('children', -1)}")


@dp.message(F.from_user.username == "awertkx")
async def alnur_message_handler(message: Message):
    if check_private_chat(message):
        await message.answer(f"СУка кто пишет в лс тот педик ебаный")
        return
    children_addition = random.randint(1, 10)
    data = load_database()

    temp_children = data.get('temp_children', -1) + children_addition
    data["temp_children"] = temp_children
    data["children"] += children_addition
    data["alnur_mesage_count"] = data.get("alnur_mesage_count", 0) + 1
    save_database(data)
    if data.get("alnur_mesage_count", 0) % 10 == 0:
        data["temp_children"] = 0
        save_database(data)
        await message.answer(f"Количество детей в подвале пополнено на {temp_children}")  


@dp.message(F.text == '#МыХотимТрахнутьАльнура!')
async def trah_message_handler(message: Message):
    if check_private_chat(message):
        await message.answer(f"СУка кто пишет в лс тот педик ебаный")
        return
    data = load_database()
    data['trah'] = True
    save_database(data)

@dp.message(F.text == '#МожешьОтдохнутьАльнур')
async def trah_end_message_handler(message: Message):
    if check_private_chat(message):
        await message.answer(f"СУка кто пишет в лс тот педик ебаный")
        return
    data = load_database()

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
    if check_private_chat(message):
        await message.answer(f"СУка кто пишет в лс тот педик ебаный")
        return
    data = load_database()
    if data.get("children", -1) == 0:
        await message.answer("Подвал пуст (пока)")
        return
    
    save_number = random.randint(1, 6)
    data['save_number'] = save_number
    save_database(data)
    
    await message.answer(f"Чтобы спасти детей выбейте {save_number} на кубике!")

@dp.message(Command('my_save_score'))
async def my_save_score(message: Message) -> None:
    try:
        users = load_users()
        response = await message.answer(f"Ты спас {users.get(message.from_user.id, {}).get('save_score', -1)} детей")
        await asyncio.sleep(60)
    
        await bot.delete_message(chat_id=response.chat.id, message_id=response.message_id)
    except:
        print('my_save_score exception')
        
@dp.message(Command('save_leaderboard'))
async def save_leaderboard(message: Message) -> None:
    users = load_users()
    sorted_users = sorted(users.items(), key=lambda x: x[1]['save_score'], reverse=True)
    response_text = "🏅 Топ спасителей:\n\n"
    emojis = ["🥇", "🥈", "🥉"]
    for index, (_, data) in enumerate(sorted_users):
        emoji = emojis[index] if index < 3 else "       "
        response_text += f"{emoji} @{data.get('user_name', 'Unknown')}: {data.get('save_score', -1)} детей\n"
    
    response = await message.answer(response_text)
    await asyncio.sleep(60)

    await bot.delete_message(chat_id=response.chat.id, message_id=response.message_id)

@dp.message(Command('my_rps_streak'))
async def my_rps_streak(message: Message) -> None:
    users = load_users()
    response = await message.answer(f"Твой стрик в КНБ: {users[message.from_user.id].get('rps_streak', 0.5)-0.5}")
    await asyncio.sleep(60)

    await bot.delete_message(chat_id=response.chat.id, message_id=response.message_id)
@dp.message(F.dice)
async def dice_handler(message: Message) -> None:
    if check_private_chat(message):
        await message.answer(f"СУка кто пишет в лс тот педик ебаный")
        return
    current_time = datetime.datetime.now(datetime.timezone.utc)
    data = load_database()
    if data.get("children", -1) == 0:
        await message.answer("Подвал пуст (пока)")
        return
    users = load_users()
    if message.from_user.id not in users:
        users = create_user(message.from_user.id, message.from_user.username)
    user_id = message.from_user.id
    
    user_data = users.get(user_id, {})
    last_roll_time = user_data.get("cooldown_time")
    if last_roll_time:
        cooldown_end_time = last_roll_time + COOLDOWN_PERIOD
        if current_time < cooldown_end_time:
            if user_data.get("free_spins", 0) > 0:
                users[user_id]["free_spins"] -= 1
                current_time = user_data.get("cooldown_time")
                await message.answer(f"@{message.from_user.username} потратил 1 фриспин! Осталось {user_data['free_spins']} фриспинов!")
            else:
                remaining_time = cooldown_end_time - current_time
                remaining_minutes = remaining_time.total_seconds() // 60
                remaining_seconds = remaining_time.total_seconds() % 60
                await message.answer(f"Подожди {int(remaining_minutes)} минут и {int(remaining_seconds)} секунд!")
                return
    users[user_id]["cooldown_time"] = current_time
    
    if message.dice.value == data.get('save_number', -1):
        precent = int((users.get(user_id, {}).get("rps_streak", 1) / 10) * 100)
        if precent > 100:
            print_children = data.get("children")
        else:
            print_children = int(data["children"] * (users.get(user_id, {}).get("rps_streak", 1) / 10))
        data["children"] -= print_children
        data["temp_children"] = 0
        save_score = users[user_id].get("save_score", 0) + print_children
        users[user_id]["save_score"] = save_score
        users[user_id]["rps_streak"] = 0.5
        if message.from_user.username == "awertkx":
            data["children"] = 0
            await message.answer("Ебать, Альнур решил отпустить всех своих заключенных, видимо сбор намечается.")
        else:
            if message.from_user.username:
                await message.answer(f"Ахуеть, вы спасли {print_children} детей! Похлопаем @{message.from_user.username}!")
            else:
                await message.answer(f"Ахуеть, вы спасли {print_children} детей! Алим бля тег себе сделай заебал уже.")
        save_database(data)
    else:
        unluck_number = random.randint(10, 100)
        data["children"] = data["children"] + unluck_number
        save_database(data)
        await message.answer(f"Вы проиграли! Альнур узнал о ваших намерениях и словил еще {unluck_number} детей!")
    save_users(users)

        
@dp.message()
async def echo_handler(message: Message) -> None: 
    data = load_database()
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