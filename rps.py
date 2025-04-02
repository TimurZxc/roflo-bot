from aiogram import Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import datetime
import asyncio
import random
from utils import *
from bot import bot

# Game session storage
game_sessions = {}

def game_ender(winer_id,winer_username, loser_id,loser_username, tie):
    users = load_users()
    if tie:
        if winer_id in users:
            users[winer_id]['free_spins'] -= 2
        else:
            users = create_user(winer_id, winer_username)
            users[winer_id]['free_spins'] -= 2
        if loser_id in users:
            users[loser_id]['free_spins'] -= 2
        else:
            users = create_user(loser_id, loser_username)
            users[loser_id]['free_spins'] -= 2
        save_users(users)
        return   
    if winer_id in users:
        users[winer_id]['free_spins'] += 3
        users[winer_id]['rps_streak'] += 1
    else:
        users = create_user(winer_id, winer_username)
        users[winer_id]['free_spins'] += 3
        users[winer_id]['rps_streak'] += 1
    if loser_id in users:
        users[loser_id]['free_spins'] -= 3
        users[loser_id]['rps_streak'] = 0.5
    else:
        users = create_user(loser_id, loser_username)
        users[loser_id]['free_spins'] = 0
        users[loser_id]['rps_streak'] = 0.5
    save_users(users)
def determine_winner(choice1, choice2):
    if choice1 == choice2:
        return None
    elif (choice1 == 'камень' and choice2 == 'ножницы') or \
         (choice1 == 'ножницы' and choice2 == 'бумага') or \
         (choice1 == 'бумага' and choice2 == 'камень'):
        return 'player1'
    else:
        return 'player2'

async def start_rps_handler(message: Message) -> None:
    if await is_user_spamming(message.from_user.id):
        await mute_user(message.chat.id, message.from_user.id)
        await message.answer(f"@{message.from_user.username} получил кляп за спам блять")
        return
    if check_private_chat(message):
        await message.answer(f"СУка кто пишет в лс тот педик ебаный")
        return
    if message.chat.id in game_sessions:
        msg = await message.answer("Игра уже в процессе!")
        asyncio.create_task(delete_message_later(msg))
        return
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)

    if member.status != 'administrator' and member.status != 'creator':    
        await bot.promote_chat_member(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            can_change_info=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_video_chats=False,
            is_anonymous=False 
        )
    game_sessions[message.chat.id] = {'player1': message.from_user.id, 
                                      'player2': None, 
                                      'player1_choice': None, 
                                      'player2_choice': None,
                                      'player1_username': message.from_user.username,
                                      'player2_username': None}
    
    start_msg = await message.answer(f"@{message.from_user.username} начал КНБ! Чтобы принять вызов - /rps_join.")
    game_sessions[message.chat.id]['start_msg'] = start_msg


async def rps_status_handler(message: Message) -> None:
    if await is_user_spamming(message.from_user.id):
        await mute_user(message.chat.id, message.from_user.id)
        await message.answer(f"@{message.from_user.username} получил кляп за спам блять")
        return
    session = game_sessions.get(message.chat.id)
    if check_private_chat(message):
        await message.answer("СУка кто пишет в лс тот педик ебаный")
        return 

    if message.chat.id not in game_sessions:
        msg = await message.answer("Нет активных игр! Начните игру с /rps_start")
        asyncio.create_task(delete_message_later(msg))
    else:
        if not session['player2']:
            msg =await message.answer(f"@{session['player1_username']} в ожидании соперника! Чтобы принять вызов - /rps_join.")
            asyncio.create_task(delete_message_later(msg))
        elif session['player2']:
            msg = await message.answer(f"@{session['player1_username']} и @{session['player2_username']} в игрe!")
            asyncio.create_task(delete_message_later(msg))
            if session['player1_choice']:
                msg = await message.answer(f"@{session['player1_username']} выбрал!")
                asyncio.create_task(delete_message_later(msg))
            else:
                msg = await message.answer(f"@{session['player1_username']} еще нихуя не выбрал!")
                asyncio.create_task(delete_message_later(msg))
            if session['player2_choice']:
                msg = await message.answer(f"@{session['player2_username']} выбрал!")
                asyncio.create_task(delete_message_later(msg))
            else:
                msg = await message.answer(f"@{session['player2_username']} еще нихуя не выбрал!")
                asyncio.create_task(delete_message_later(msg))

async def join_rps_handler(message: Message) -> None:
    if await is_user_spamming(message.from_user.id):
        await mute_user(message.chat.id, message.from_user.id)
        await message.answer(f"@{message.from_user.username} получил кляп за спам блять")
        return
    if check_private_chat(message):
        await message.answer("СУка кто пишет в лс тот педик ебаный")
        return
    session = game_sessions.get(message.chat.id)
    

    if not session:
        msg = await message.answer("Нету активных игр! Начните игру с /rps_start")
        asyncio.create_task(delete_message_later(msg))
        return

    if session['player2']:
        msg = await message.answer("В этой игре уже 2 игрока!")
        asyncio.create_task(delete_message_later(msg))
        return
    if message.from_user.id == session['player1']:
        msg = await message.answer(f"@{message.from_user.username} уже в игре сука!")
        asyncio.create_task(delete_message_later(msg))
        return
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if member.status != 'administrator' and member.status != 'creator':    
        await bot.promote_chat_member(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            can_change_info=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_video_chats=False,
            is_anonymous=False 
        )
    session['player2'] = message.from_user.id
    session['player2_username'] = message.from_user.username
    msg = await message.answer(f"@{session['player2_username']} вошел в игру! Оба игрока должны сделать свой выбор.")
    asyncio.create_task(delete_message_later(msg))
    asyncio.create_task(delete_message_later(session['start_msg'], 5))

    choice_buttons = choice_buttons = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🪨", callback_data="rps_choice_камень"),
            InlineKeyboardButton(text="✂️", callback_data="rps_choice_ножницы"),
            InlineKeyboardButton(text="🧻", callback_data="rps_choice_бумага")
        ]
    ])

    buttons_msg = await message.answer(f"@{session['player1_username']} и @{session['player2_username']}, нажмите кнопки бля", reply_markup=choice_buttons)
    session['buttons_message'] = buttons_msg

async def callback_rps_choice_handler(callback_query: CallbackQuery) -> None:
    session = game_sessions.get(callback_query.message.chat.id)
    player_id = callback_query.from_user.id

    if not session:
        msg = await callback_query.answer("Нет активных игр! Начните игру с /rps_start", show_alert=True)
        asyncio.create_task(delete_message_later(msg))
        return

    if player_id != session['player1'] and player_id != session['player2']:
        msg = await callback_query.answer("Ты не игрок этой игры!", show_alert=True)
        asyncio.create_task(delete_message_later(msg))
        return

    choice = callback_query.data.split("_")[2]

    if player_id == session['player1']:
        session['player1_choice'] = choice
        msg = await callback_query.message.answer(f"@{session['player1_username']} выбрал!")
        asyncio.create_task(delete_message_later(msg))
    elif player_id == session['player2']:
        session['player2_choice'] = choice
        msg = await callback_query.message.answer(f"@{session['player2_username']} выбрал!")
        asyncio.create_task(delete_message_later(msg))

    if session['player1_choice'] and session['player2_choice']:
        winner = determine_winner(session['player1_choice'], session['player2_choice'])
        if winner == 'player1':
            try:
                await bot.set_chat_administrator_custom_title(
                    chat_id=callback_query.message.chat.id,
                    user_id=session['player2'],
                    custom_title="Педик"
                )
            except TelegramBadRequest:
                print(TelegramBadRequest)
            try:
                await bot.set_chat_administrator_custom_title(
                    chat_id=callback_query.message.chat.id,
                    user_id=session['player1'],
                    custom_title="admin"
                )
            except TelegramBadRequest:
                print(TelegramBadRequest)
            game_ender(session['player1'],session["player1_username"], session['player2'],session["player2_username"], False)
            msg = await callback_query.message.answer(f"@{session['player1_username']} победил, и получает 3 фри спина!")
            asyncio.create_task(delete_message_later(msg))
            msg = await callback_query.message.answer(f"@{session['player2_username']} проебал, и получает -3 фри спина + статус педик")
            asyncio.create_task(delete_message_later(msg))
        elif winner == 'player2':
            try:
                await bot.set_chat_administrator_custom_title(
                    chat_id=callback_query.message.chat.id,
                    user_id=session['player1'],
                    custom_title="Педик"
                )
            except TelegramBadRequest:
                print(TelegramBadRequest)
            try:
                await bot.set_chat_administrator_custom_title(
                    chat_id=callback_query.message.chat.id,
                    user_id=session['player2'],
                    custom_title="admin"
                )
            except TelegramBadRequest:
                print(TelegramBadRequest)
            game_ender(session['player2'],session["player2_username"], session['player1'],session["player1_username"], False)
            msg = await callback_query.message.answer(f"@{session['player2_username']} победил, и получает 3 фри спина!")
            asyncio.create_task(delete_message_later(msg))
            msg = await callback_query.message.answer(f"@{session['player1_username']} проебал, и получает -3 фри спина + статус педик")
            asyncio.create_task(delete_message_later(msg))
        else:
            data = load_database()
            unluck_number = random.randint(10, 100)
            data["children"] = data["children"] + unluck_number
            save_database(data)
            msg = await callback_query.message.answer(f"Ничья! Оба получают -2 фриспина, а Aльнур выходит на охоту и ловит {unluck_number} детей")
            game_ender(session['player1'], session["player1_username"], session['player2'], session["player2_username"], True)
            asyncio.create_task(delete_message_later(msg))
        if session['buttons_message']:
            asyncio.create_task(delete_message_later(session['buttons_message'], 5))
        del game_sessions[callback_query.message.chat.id] 
    await callback_query.answer()  
async def cancel_rps_handler(message: Message) -> None:
    if await is_user_spamming(message.from_user.id):
        await mute_user(message.chat.id, message.from_user.id)
        await message.answer(f"@{message.from_user.username} получил кляп за спам блять")
        return
    if check_private_chat(message):
        await message.answer(f"СУка кто пишет в лс тот педик ебаный")
        return
    if message.chat.id in game_sessions:
        if game_sessions[message.chat.id]['player1'] == message.from_user.id or game_sessions[message.chat.id]['player2'] == message.from_user.id:
            asyncio.create_task(delete_message_later(game_sessions[message.chat.id]['start_msg'], 5))
            del game_sessions[message.chat.id]
            msg = await message.answer("Игра отменена")
            asyncio.create_task(delete_message_later(msg))
        else:
            msg = await message.answer("Вы не игрок этой игры!")
            asyncio.create_task(delete_message_later(msg))
    else:
        msg = await message.answer("Нет игры для отмены")
        asyncio.create_task(delete_message_later(msg))

# Function to register all handlers
def register_handlers_rps(dp: Dispatcher):
    dp.message.register(start_rps_handler, Command('rps_start'))
    dp.message.register(join_rps_handler, Command('rps_join'))
    # dp.message.register(choice_rps_handler, Command('rps_choice'))
    dp.message.register(cancel_rps_handler, Command('rps_cancel'))
    dp.message.register(rps_status_handler, Command('rps_status'))
    dp.callback_query.register(callback_rps_choice_handler, lambda c: c.data and c.data.startswith("rps_choice_"))
