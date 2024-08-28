import datetime
import json
import asyncio
from aiogram.types import Message
from bot import bot

COOLDOWN_FILE = "user_cooldowns.json"
DATABASE_FILE = "database.json"
COOLDOWN_PERIOD = datetime.timedelta(hours=1)

async def delete_message_later(message: Message, delay: int = 60):
    await asyncio.sleep(delay)
    await message.delete()

    
def create_user(user_id, user_name):
    users = load_users()
    users[user_id] = {
        "cooldown_time": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1),
        "free_spins": 0,
        "save_score": 0,
        "rps_streak": 0.5,
        "user_name": user_name
    }
    save_users(users)
    return users
def check_private_chat(message):
    if message.chat.type == 'private':
        return True
    else:
        return False
def load_users():
    try:
        with open(COOLDOWN_FILE, "r") as f:
            cooldowns = json.load(f)
            return {int(k): {
                        "cooldown_time": datetime.datetime.fromisoformat(v["cooldown_time"]),
                        "free_spins": v["free_spins"],
                        "save_score": v["save_score"],
                        "rps_streak": v["rps_streak"],
                        "user_name": v["user_name"]
                    } for k, v in cooldowns.items()}
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

# Save cooldown data to JSON file
def save_users(json_data):
    with open(COOLDOWN_FILE, "w") as f:
        json.dump({
            k: {
                "cooldown_time": v["cooldown_time"].isoformat(),
                "free_spins": max(v["free_spins"], 0),
                "save_score": max(v["save_score"], 0),
                "rps_streak": max(v["rps_streak"], 0),
                "user_name": v["user_name"]
            } for k, v in json_data.items()
        }, f, indent=4)

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