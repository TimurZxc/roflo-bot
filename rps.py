from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import datetime
from utils import load_users, check_private_chat, save_users, create_user, delete_message_later

# Game session storage
game_sessions = {}

def give_reward(player_id):
    users = load_users()
    print(users)

    if player_id in users:
        users[player_id]['free_spins'] += 3
    else:
        users = create_user(player_id)
        users[player_id]['free_spins'] += 3
    save_users(users)
    print(users, "\n",  users[player_id]['free_spins'])

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
    if check_private_chat(message):
        await message.answer(f"СУка кто пишет в лс тот педик ебаный")
        return
    if message.chat.id in game_sessions:
        await message.answer("Игра уже в процессе!")
        return

    game_sessions[message.chat.id] = {'player1': message.from_user.id, 
                                      'player2': None, 
                                      'player1_choice': None, 
                                      'player2_choice': None,
                                      'player1_username': message.from_user.username,
                                      'player2_username': None}

    await message.answer(f"@{message.from_user.username} начал КНБ! Чтобы принять вызов - /rps_join.")
    

async def join_rps_handler(message: Message) -> None:
    if check_private_chat(message):
        await message.answer("СУка кто пишет в лс тот педик ебаный")
        return
    session = game_sessions.get(message.chat.id)

    if not session:
        await message.answer("Нету активных игр! Начните игру с /rps_start")
        return

    if session['player2']:
        await message.answer("В этой игре уже 2 игрока!")
        return
    if message.from_user.id == session['player1']:
        await message.answer(f"@{message.from_user.username} уже в игре сука!")
        return

    session['player2'] = message.from_user.id
    session['player2_username'] = message.from_user.username
    await message.answer(f"@{session['player2_username']} вошел в игру! Оба игрока должны сделать свой выбор.")

    # Send buttons to both players to make their choice
    choice_buttons = choice_buttons = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🪨", callback_data="rps_choice_камень"),
            InlineKeyboardButton(text="✂️", callback_data="rps_choice_ножницы"),
            InlineKeyboardButton(text="🧻", callback_data="rps_choice_бумага")
        ]
    ])

    await message.answer(f"@{session['player1_username']} и @{session['player2_username']}, нажмите кнопки бля", reply_markup=choice_buttons)

async def choice_rps_handler(message: Message) -> None:
    if check_private_chat(message):
        await message.answer(f"СУка кто пишет в лс тот педик ебаный")
        return
    session = game_sessions.get(message.chat.id)

    if not session:
        await message.answer("Нету активных игр! Начните игру с /rps_start")
        return

    player_id = message.from_user.id
    if player_id != session['player1'] and player_id != session['player2']:
        await message.answer("Вы не игрок этой игры!")
        return
    if len(message.text.split()) < 2:
        await message.answer("Неверно введена команда блять нахуй блять, надо - /rps_choice камень | ножницы | бумага")
        return
    else:
        choice = message.text.split()[1].lower()
        
    if choice not in ['камень', 'ножницы', 'бумага']:
        await message.answer("Еблан?")
        return

    if player_id == session['player1']:
        session['player1_choice'] = choice
        await message.answer(f"@{session['player1_username']} выбрал!")
    elif player_id == session['player2']:
        session['player2_choice'] = choice
        await message.answer(f"@{session['player2_username']} выбрал!")

    if session['player1_choice'] and session['player2_choice']:
        winner = determine_winner(session['player1_choice'], session['player2_choice'])
        print(winner, session['player1_choice'], session['player2_choice'])
        if winner == 'player1':
            give_reward(session['player1'])
            await message.answer(f"@{session['player1_username']} победил, и получает 3 фри спина!")
        elif winner == 'player2':
            give_reward(session['player2'])
            await message.answer(f"@{session['player2_username']} победил, и получает 3 фри спина!")
        else:
            await message.answer("Ничья!")

        del game_sessions[message.chat.id]  # End the game session after the result
async def callback_rps_choice_handler(callback_query: CallbackQuery) -> None:
    session = game_sessions.get(callback_query.message.chat.id)
    player_id = callback_query.from_user.id

    if not session:
        await callback_query.answer("Нет активных игр! Начните игру с /rps_start", show_alert=True)
        return

    if player_id != session['player1'] and player_id != session['player2']:
        await callback_query.answer("Ты не игрок этой игры!", show_alert=True)
        return

    choice = callback_query.data.split("_")[2]  # Extracting the choice from callback data

    if player_id == session['player1']:
        session['player1_choice'] = choice
        await callback_query.message.answer(f"@{session['player1_username']} выбрал!")
    elif player_id == session['player2']:
        session['player2_choice'] = choice
        await callback_query.message.answer(f"@{session['player2_username']} выбрал!")

    # Check if both players have made their choice
    if session['player1_choice'] and session['player2_choice']:
        winner = determine_winner(session['player1_choice'], session['player2_choice'])
        if winner == 'player1':
            give_reward(session['player1'])
            await callback_query.message.answer(f"@{session['player1_username']} победил, и получает 3 фри спина!")
        elif winner == 'player2':
            give_reward(session['player2'])
            await callback_query.message.answer(f"@{session['player2_username']} победил, и получает 3 фри спина!")
        else:
            await callback_query.message.answer("Ничья!")

        del game_sessions[callback_query.message.chat.id] 
    await callback_query.answer()  
async def cancel_rps_handler(message: Message) -> None:
    if check_private_chat(message):
        await message.answer(f"СУка кто пишет в лс тот педик ебаный")
        return
    if message.chat.id in game_sessions:
        if game_sessions[message.chat.id]['player1'] == message.from_user.id or game_sessions[message.chat.id]['player2'] == message.from_user.id:
            del game_sessions[message.chat.id]
            await message.answer("Игра отменена")
        else:
            await message.answer("Вы не игрок этой игры!")
    else:
        await message.answer("Нет игры для отмены")

# Function to register all handlers
def register_handlers_rps(dp: Dispatcher):
    dp.message.register(start_rps_handler, Command('rps_start'))
    dp.message.register(join_rps_handler, Command('rps_join'))
    dp.message.register(choice_rps_handler, Command('rps_choice'))
    dp.message.register(cancel_rps_handler, Command('rps_cancel'))
    dp.callback_query.register(callback_rps_choice_handler, lambda c: c.data and c.data.startswith("rps_choice_"))
