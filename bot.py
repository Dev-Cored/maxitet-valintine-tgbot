import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.filters import Command, StateFilter
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import random as r
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

import sqlite3
import hashlib

from database import *

logging.basicConfig(level=logging.INFO)

init_db()

#==========================================================================================================================================
# Генераторы

BOT_USERNAME = "maxitet_family_valentines_bot"
def gen_ref_url(user_id):
    ref_code = "ref_"+ hashlib.md5(str(user_id).encode()).hexdigest()[:15]
    return f"https://t.me/{BOT_USERNAME}?start={ref_code}"

def gen_ref_code(user_id):
    ref_code = "ref_" + hashlib.md5(str(user_id).encode()).hexdigest()[:15]
    return ref_code

#==========================================================================================================================================
# Клавиатуры и кнопки

def change_text_btn():
    btns = [
        [types.InlineKeyboardButton(text="🎲 Изменить текст на случайный 🎲", callback_data="change_valentine_text")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=btns)
    return keyboard

def menu_keyboard():
    kb = [
        [types.KeyboardButton(text="💌 Отправить валентинку")],
        [types.KeyboardButton(text="🔗 Моя реферальная ссылка"),
         types.KeyboardButton(text="📈 Моя статистика")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие",
        one_time_keyboard=True
    )

    return keyboard

def y_n_keyboard():
    kb = [
        [
            types.KeyboardButton(text="Да!"),
            types.KeyboardButton(text="Нет!")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Подтвердить?",
        one_time_keyboard=True
    )
    return keyboard

#==========================================================================================================================================
# Статусы

class StatesValentine(StatesGroup):
    waiting_for_username = State()
    waiting_for_valentine_text = State()
    waiting_for_anonimise = State()
    waiting_for_accept = State()

class StatesValentineRef(StatesGroup):
    waiting_for_valentine_text = State()
    waiting_for_anonimise = State()
    waiting_for_accept = State()

#==========================================================================================================================================
# Роутеры

menu_router = Router()
valentine_create = Router()
ref_valentine_create = Router()
reg_user = Router()

#==========================================================================================================================================
# Старт бота

with open('token.txt') as f:
    TOKEN = f.read().strip()

bot = Bot(token=TOKEN)
dp = Dispatcher()

#==========================================================================================================================================
# Стартовая команда
@dp.message(Command('start'))
async def start_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.username
    ref_url = gen_ref_code(user_id)

    recently_reg = reg_start_user(user_id, user_name, ref_url)

    args = message.text.split()

    if len(args) > 1:
        ref_code = args[1]
        await message.answer(f"🔗 Вы перешли по реферальной ссылке чтобы написать валентинку!")
        ref_user = check_ref_user_in_db(ref_code)

        if ref_user == None:
            await message.answer("К сожалению, ссылка не действительна! Не удалось найти пользователя, кому пренадлежит эта ссылка.")
            await message.answer("Что вы хотите сделать?", reply_markup=menu_keyboard())
        else:
            await state.update_data(ref_user_id=ref_user)

            kb = [
                [types.KeyboardButton(text="🤖 Автоматически сгенерировать текст ⌨️")]
            ]
            keyboard = types.ReplyKeyboardMarkup(
                keyboard=kb,
                resize_keyboard=True,
                input_field_placeholder="Введите текст валентинки...")
            await message.answer("А теперь напиши, что ты хочешь передать человеку в валентинке, или же ты можешь оставить автоматически сгенерированное сообщение. Введи свое сообщение или нажми кнопку для автоматического заполнения: ", reply_markup=keyboard)

            await state.set_state(StatesValentineRef.waiting_for_anonimise)
            return await ref_valentine_create.message.trigger(message)

        await message

    else:
        if recently_reg:
            await message.answer("👋 Тебя приветсвует бот Валентинок от канала В Макситете Любят!\n"+
                                 "При помощи бота можно на выбор, анонимно или нет, отправить валентинку твоей второй половинке или другу/подруге.")
            await message.answer("📔**Инструкция**\n\nИнструкция проста как мир:\n"+
                                 "❤️ - Чтобы отправить валентинку, нужно нажать кнопочку `💌Отправить валентинку` и заполнить форму.\n"+
                                 "📩 - Чтобы получить валентинку, необходимо всего навсего отправить /start боту, что ты уже и сделал")
            await message.answer("⁉️**Частые вопросы**\n\n"+
                                 "- **Как отправить валентинку другу/подруге?**\n"+
                                 "Чтобы отправить другу/подруге валентинку нужно знать его/ее юзернейм в Телеграме (начинается с @), а так же что бы он/она так же хотя бы раз запускал(а) бота. Так же можно воспользоваться реферальной ссылкой, которая выдается каждому при первом запуске бота, а так же ее можно посмотреть нажав на кнопку '🔗 Моя реферальная ссылка'\n\n"+
                                 "- **Что если у меня/у моего друга(подруги) нету юзер нейма?**\n"+
                                 "В таком случае остается только пользоваться реферальным кодом.")
            await message.answer("💡**Советы**\n"+
                                 "- Размещайте свою реферальную ссылку у себя в профиле, в своем ТГК, или просто делитесь ей со своими друзьями.\n"+
                                 "- Если вы отправили валентинку но адресат не зашел в бота, то напишите в предложку макситета с ссылкой на пользователя и мы вежливо и анонимно попросим посмотреть)")

        await message.answer("Что вы хотите сделать?", reply_markup=menu_keyboard())
        return await menu_router.message.trigger(message)


#==========================================================================================================================================
# Обработка кнопок главного меню

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

#==========================================================================================================================================
# Отправка валентинки из меню

@valentine_create.message(StatesValentine.waiting_for_username)
async def get_valentine_username_to(message: types.Message, state: FSMContext):
    username = message.text.replace("@", "")
    user_from_id = message.from_user.id
    if username == message.from_user.username:
        await message.answer("Нельзя отправить валентинку самому себе!")
    else:
        await state.update_data(user_from_id=user_from_id)
        await state.update_data(user_name_to=username)
        user_in_db, user_id_for = check_user_id_db(username)
        if user_in_db:
            await message.answer("Пользователь найден в базе! Он получит валентинку моментально!")
            await state.update_data(user_in_db=True)
            await state.update_data(user_id_to=user_id_for)
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
    await message.answer("Отлично! Теперь скажи, хочешь отправить валентинку от введенного, или анонимно, нажав на кнопку?", reply_markup=keyboard)
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

    if valentine_text == "generate_auto":
        valentine_text = valentine_random_text[r.randint(0, len(valentine_random_text)-1)]
        await state.update_data(valentine_text=valentine_text)
        await message.answer(f"Твоя валентинка будет выглядеть так:\nОт: {user_from}\nКому: @{user_to}\nНадпись на валентинке: {valentine_text}", reply_markup=change_text_btn())
    else:
        await message.answer(f"Твоя валентинка будет выглядеть так:\nОт: {user_from}\nКому: @{user_to}\nНадпись на валентинке: {valentine_text}")

    await message.answer("Подтвердить отправку валентинки?", reply_markup=y_n_keyboard())
    await state.set_state(StatesValentine.waiting_for_accept)


@valentine_create.message(StatesValentine.waiting_for_accept)
async def y_or_n_send_valentine(message: types.Message, state: FSMContext):
    print("Нажата кнопка")
    text = message.text

    if text == "Да!":
        valentine_data = await state.get_data()
        user_to = valentine_data['user_name_to']
        valentine_text = valentine_data['valentine_text']
        user_from_name = valentine_data['user_from_name']
        send_momental = valentine_data['user_in_db']
        user_id_for = valentine_data['user_id_to']
        user_from_id = valentine_data['user_from_id']

        if user_from_name == "anonimous":
            anonimous = True
        else:
            anonimous = False

        if send_momental:
            send_valentine_to_db(user_from_id, user_to, valentine_text, anonimous, send_momental, user_from_name, user_id_for)
            await bot.send_message(chat_id=user_id_for, text="Тебе отправили валентинку!")
            await message.answer("Валентинка доставлена!")


    elif text == "Нет!":
        await message.answer("Отправка валентинки прервана!", reply_markup=menu_keyboard())
        return await menu_router.message.trigger(message)

    else:
        await message.answer("Введите да или нет!")

#==========================================================================================================================================
# Отправка валентинки по реферальной ссылке

@ref_valentine_create.message(StatesValentineRef.waiting_for_valentine_text)
async def ref_valentine_text(message: types.Message, state: FSMContext):
    text = message.text

    if text == "🤖 Автоматически сгенерировать текст ⌨️":
        await state.update_data(valentine_texts="generate_auto")
    else:
        await state.update_data(valentine_texts=text)

    kb = [
        [types.KeyboardButton(text="🥷 Отправить анонимно 🥷")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Подпиши себя..."
    )
    await message.answer("Отлично! Теперь скажи, хочешь отправить валентинку от введенного, или анонимно, нажав на кнопку?", reply_markup=keyboard)
    await state.set_state(StatesValentineRef.waiting_for_anonimise)

@ref_valentine_create.message(StatesValentineRef.waiting_for_anonimise)
async def ref_user_name_from(message: types.Message, state: FSMContext):
    text = message.text

    if text == "🥷 Отправить анонимно 🥷":
        await state.update_data(user_name_from="anonimous")
    else:
        await state.update_data(user_name_from=text)

    valentine_data = await state.get_data()
    user_to = valentine_data['ref_user_id']
    valentine_text = valentine_data['valentine_texts']
    user_from = valentine_data['user_from_name']

    if valentine_text == "generate_auto":
        valentine_text = valentine_random_text[r.randint(0, len(valentine_random_text)-1)]
        await state.update_data(valentine_text=valentine_text)
        await message.answer(f"Твоя валентинка будет выглядеть так:\nОт: {user_from}\nКому: @{user_to}\nНадпись на валентинке: {valentine_text}", reply_markup=change_text_btn())
    else:
        await message.answer(f"Твоя валентинка будет выглядеть так:\nОт: {user_from}\nКому: @{user_to}\nНадпись на валентинке: {valentine_text}")

    await message.answer("Подтвердить отправку валентинки?", reply_markup=y_n_keyboard())
    await state.set_state(StatesValentineRef.waiting_for_accept)

@valentine_create.message(StatesValentineRef.waiting_for_accept)
async def y_or_n_send_valentine(message: types.Message, state: FSMContext):
    text = message.text

    if text == "Да!":
        valentine_data = await state.get_data()
        user_to = valentine_data['user_name_to']
        valentine_text = valentine_data['valentine_text']
        user_from = valentine_data['user_from_name']
        send_momental = valentine_data['user_in_db']
        user_id_for = valentine_data['ref_user_id']

        if user_from == "anonimous":
            anonimous = True
        else:
            anonimous = False

        if send_momental:
            send_valentine_to_db(user_from, user_to, valentine_text, anonimous, send_momental,user_from, user_id_for)
            await bot.send_message(chat_id=user_id_for, text=f"Тебе отправили валентинку!\nОт: {user_from}\nТекст на валентинке: {valentine_text}")
        else:
            send_valentine_to_db(user_from, user_to, valentine_text, anonimous, send_momental, user_from, user_id_for)
            await message.answer("Валентинка сохранена! Пользователь получит ее при первой активации бота!")
    elif text == "Нет!":
        await message.answer("Отправка валентинки прервана!", reply_markup=menu_keyboard())
        return await menu_router.message.trigger(message)
    else:
        await message.answer("Введите да или нет!")

#==========================================================================================================================================
# Обработки инлайн кнопок

@dp.callback_query(F.data == "change_valentine_text")
async def change_valentine_text(call: types.CallbackQuery, state: FSMContext):
    # print("Нажата кнопка")
    valentine_data = await state.get_data()
    user_to = valentine_data['user_name_to']
    user_from = valentine_data['user_from_name']

    valentine_text = valentine_random_text[r.randint(0, len(valentine_random_text)-1)]
    await state.update_data(valentine_text=valentine_text)

    await call.message.edit_text(f"Твоя валентинка будет выглядеть так:\nОт: {user_from}\nКому: @{user_to}\nНадпись на валентинке: {valentine_text}", reply_markup=change_text_btn())
    await call.answer()



#==========================================================================================================================================
# Инициализация бота

async def main():
    dp.include_router(menu_router)
    dp.include_router(valentine_create)
    dp.include_router(ref_valentine_create)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
