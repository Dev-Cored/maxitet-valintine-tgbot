import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.filters import Command, StateFilter
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import sqlite3
import hashlib
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

#from kbs import start_keyboard
from database import *

logging.basicConfig(level=logging.INFO)

init_db()

BOT_USERNAME = "maxitet_family_valentines_bot"
def gen_ref_url(user_id):
    ref_code = "ref_"+ hashlib.md5(str(user_id).encode()).hexdigest()[:8]
    return f"https://t.me/{BOT_USERNAME}?start={ref_code}"

def gen_ref_code(user_id):
    ref_code = "ref_" + hashlib.md5(str(user_id).encode()).hexdigest()[:8]
    return ref_code

with open('token.txt') as f:
    TOKEN = f.read().strip()

bot = Bot(token=TOKEN)
dp = Dispatcher()

menu_router = Router()
valentine_create = Router()
ref_valentine_create = Router()
reg_user = Router()

class StatesValentine(StatesGroup):
    waiting_for_username = State()
    waiting_for_valentine_text = State()
    waiting_for_anonimise = State()
    waiting_for_sender_name = State()

def menu_keyboard():
    kb = [
        [types.KeyboardButton(text="💌 Отправить валентинку")],
        [types.KeyboardButton(text="🔗 Моя реферальная ссылка"),
         types.KeyboardButton(text="📈 Моя статистика")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие")
    return keyboard


@dp.message(Command('start'))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    ref_url = gen_ref_code(user_id)

    recently_reg = reg_start_user(user_id, user_name, ref_url)

    args = message.text.split()

    if len(args) > 1:
        ref_code = args[1]
        await message.answer(f"🔗 Вы перешли по реферальной чтобы написать валентинку!")
    else:
        if recently_reg:
            await message.answer("👋 Тебя приветсвует бот Валентинок от канала В Макситете Любят!\nПри помощи бота можно на выбор, анонимно или нет, отправить валентинку твоей второй половинке или другу/подруге.")
            await message.answer("📔**Инструкция**\n\nИнструкция проста как мир:\n❤️ - Чтобы отправить валентинку, нужно нажать кнопочку `💌Отправить валентинку` и заполнить форму.\n📩 - Чтобы получить валентинку, необходимо всего навсего отправить /start боту, что ты уже и сделал")
            await message.answer("⁉️**Частые вопросы**\n\n- **Как отправить валентинку другу/подруге?**\nЧтобы отправить другу/подруге валентинку нужно знать его/ее юзернейм в Телеграме (начинается с @), а так же что бы он/она так же хотя бы раз запускал(а) бота. Так же можно воспользоваться реферальной ссылкой, которая выдается каждому при первом запуске бота, а так же ее можно посмотреть нажав на кнопку '🔗 Моя реферальная ссылка'\n\n- **Что если у меня/у моего друга(подруги) нету юзер нейма?**\nВ таком случае остается только пользоваться реферальным кодом.")
            await message.answer("💡**Советы**\n- Размещайте свою реферальную ссылку у себя в профиле, в своем ТГК, или просто делитесь ей со своими друзьями.\n- Если вы отправили валентинку но адресат не зашел в бота, то напишите в предложку макситета с ссылкой на пользователя и мы вежливо и анонимно попросим посмотреть)")

        await message.answer("Что вы хотите сделать?", reply_markup=menu_keyboard())
        return await menu_router.message.trigger(message)

@menu_router.message(F.text == "🔗 Моя реферальная ссылка")
async def get_ref(message: types.Message):
    user_id = message.from_user.id
    user_ref = get_user_ref(user_id)
    await message.answer(f"Твоя реферальная ссылка: \nhttps://t.me/{BOT_USERNAME}?start={user_ref}")
    await message.answer("Что вы хотите сделать?", reply_markup=menu_keyboard())

@menu_router.message(F.text == "📈 Моя статистика")
async def user_stats(message: types.Message):
    user_id = message.from_user.id
    sent_count, get_count = get_user_stats(user_id)

    await message.answer(f"Твоя статистика:\nПолучено валентинок - {get_count}\nОтправлено валентинок - {sent_count}")
    await message.answer("Что вы хотите сделать?")

@menu_router.message(F.text == "💌 Отправить валентинку")
async def send_valentine(message: types.Message, state: FSMContext):
    await message.answer("Чтобы отправить валентинку нужно знать юзер нейм (начинается с @). \nВведите юзер нейм адресата:")
    await state.set_state(StatesValentine.waiting_for_username)
    return await valentine_create.message.trigger(message)

@valentine_create.message(StatesValentine.waiting_for_username)
async def get_valentine_username_to(message: types.Message, state: FSMContext):
    username = message.text
    await state.update_data(user_name_to=username)
    user_in_db = check_user_id_db(username)
    if user_in_db:
        await message.answer("Пользователь найден в базе! Он получит валентинку моментально!")
        await state.update_data(user_in_db=True)
    else:
        await message.answer("Пользователь пока не писал боту! Он получит твою валентинку после первой активации бота автоматически.\nЕсли ты стесняешься попросить кого-то запустить бота, то пиши в предложку канала В Макситете Любят и мы попросим за тебя)")
        await state.update_data(user_in_db=False)

    kb = [
        [types.KeyboardButton(text="🤖 Автоматически сгенерировать текст ⌨️")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Введите текст валентинки...")
    await message.answer("А теперь напиши, что ты хочешь передать человеку в валентинке, или же ты можешь оставить автоматически сгенерированное сообщение. Введи свое сообщение или нажми кнопку для автоматического заполнения: ", reply_markup=keyboard)
    await state.set_state(StatesValentine.waiting_for_valentine_text)


@valentine_create.message(StatesValentine.waiting_for_valentine_text)
async def get_valentine_text(message: types.Message, state: FSMContext):
    valentine_text = message.text
    if valentine_text == "🤖 Автоматически сгенерировать текст ⌨️":
        await state.update_data(valentine_text="generate_auto")
    else:
        await state.update_data(valentine_text=valentine_text)

    kb = [
        [types.KeyboardButton(text="🥷 Отправить анонимно 🥷")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Подпиши себя..."
    )
    await message.answer("Отлично! Теперь скажи, хочешь отправить валентинку от своего имени, или анонимно, нажав на кнопку?", reply_markup=keyboard)
    await state.set_state(StatesValentine.waiting_for_anonimise)
    return await valentine_create.message.trigger(message)

@valentine_create.message(StatesValentine.waiting_for_anonimise)
async def get_anonimise(message: types.Message, state: FSMContext):
    anonimise = message.text

    if anonimise == "🥷 Отправить анонимно 🥷":
        await state.update_data(user_from_name="anonimous")
    else:
        await state.update_data(user_from_name=anonimise)

    valentine_data = await state.get_data()
    user_to = valentine_data['user_name_to']
    valentine_text = valentine_data['valentine_text']
    user_from = valentine_data['user_from_name']



    await message.answer(f"Твоя валентинка будет выглядеть так:\nОт: {user_from}\nКому: @{user_to}\nНадпись на валентинке: {valentine_text}")
    await state.clear()
    return await menu_router.message.trigger(message)




async def main():
    dp.include_router(menu_router)
    dp.include_router(valentine_create)
    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())
