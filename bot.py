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

# Послание на утро! Добавить вызов главного меню после отправки валентинки через меню и по реферальной ссылке, а так же опять все проверить и +{сделать пост}!
# А так же почему то не прибавляется счетчик получения валентинок, проверить счетчики заново.

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

def change_text_btn(callback_data):
    btns = [
        [types.InlineKeyboardButton(text="🎲 Изменить текст на случайный 🎲", callback_data=callback_data)]
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

    recently_reg, valentine_keys = reg_start_user(user_id, user_name, ref_url)

    args = message.text.split()

    if len(args) > 1:
        ref_code = args[1]
        if recently_reg:
            await message.answer("""💖 **Привет!**  
        Тебя приветствует **бот Валентинок** от канала **["В Макситете Любят"](https://t.me/maxitet_family)**!  
        С его помощью ты можешь отправить валентинку 💌 своей второй половинке, другу или подруге — **анонимно** или **открыто**!""",
                                 parse_mode="Markdown")
            await message.answer("""
                    📜 **Инструкция**  

        🔹 **Как отправить валентинку?**  
        ❤️ Нажми кнопку "💌 Отправить валентинку" и заполни форму.  

        🔹 **Как получить валентинку?**  
        📩 Просто отправь команду **/start** — ты уже сделал первый шаг!
                    """, parse_mode="Markdown")

            await message.answer("""
                        ❓ **Частые вопросы**  

        💘 **Как отправить валентинку другу/подруге?**  
        Тебе нужен **юзернейм получателя в Telegram** (начинается с @) и чтобы получатель **хотя бы раз запустил бота**.  
        Можно также воспользоваться **реферальной ссылкой**, которую ты получаешь при первом запуске бота.  
        Чтобы найти свою ссылку, нажми "🔗 Моя реферальная ссылка".  

        💔 **Что делать, если у друга нет юзернейма?**  
        В этом случае остается только **использовать реферальную ссылку**.
                    """, parse_mode="Markdown")

            await message.answer("""
                    💡 **Полезные советы**  

        ✨ Размещай свою **реферальную ссылку** в профиле, в своем **ТГК** или просто **делись с друзьями**!  
        ✨ Если ты отправил валентинку, но получатель **не зашел в бота**, **напиши в предложку канала "[В Макситете Любят](https://t.me/anonaskbot?start=Maxitet)"** со ссылкой на пользователя** — мы вежливо и **анонимно** напомним заглянуть!
                    """, parse_mode="Markdown")

        await message.answer(f"🔗 Вы перешли по реферальной ссылке чтобы написать валентинку!")
        ref_user = check_ref_user_in_db(ref_code)

        if ref_user == None:
            await message.answer("К сожалению, ссылка не действительна! Не удалось найти пользователя, кому пренадлежит эта ссылка.")
            await message.answer("❣️ **Выбери действие:** ❣️", parse_mode="Markdown", reply_markup=menu_keyboard())
        else:
            await state.update_data(ref_user_id=ref_user)

            kb = [
                [types.KeyboardButton(text="📜 Автозаполнение")]
            ]
            keyboard = types.ReplyKeyboardMarkup(
                keyboard=kb,
                resize_keyboard=True,
                input_field_placeholder="Введите текст валентинки...")
            await message.answer("""💬 **Напиши своё сообщение!**  
Ты можешь написать текст сам или использовать автоматически сгенерированное послание.  
📝 **Введи своё сообщение** или нажми кнопку "📜 Автозаполнение".""", parse_mode="Markdown", reply_markup=keyboard)

            await state.set_state(StatesValentineRef.waiting_for_valentine_text)
            return await ref_valentine_create.message.trigger(message)

        await message

    else:
        if recently_reg:
            await message.answer("""💖 **Привет!**  
Тебя приветствует **бот Валентинок** от канала **["В Макситете Любят"](https://t.me/maxitet_family)**!  
С его помощью ты можешь отправить валентинку 💌 своей второй половинке, другу или подруге — **анонимно** или **открыто**!""", parse_mode="Markdown")
            await message.answer("""
            📜 **Инструкция**  

🔹 **Как отправить валентинку?**  
❤️ Нажми кнопку "💌 Отправить валентинку" и заполни форму.  

🔹 **Как получить валентинку?**  
📩 Просто отправь команду **/start** — ты уже сделал первый шаг!
            """, parse_mode="Markdown")

            await message.answer("""
                ❓ **Частые вопросы**  

💘 **Как отправить валентинку другу/подруге?**  
Тебе нужен **юзернейм получателя в Telegram** (начинается с @) и чтобы получатель **хотя бы раз запустил бота**.  
Можно также воспользоваться **реферальной ссылкой**, которую ты получаешь при первом запуске бота.  
Чтобы найти свою ссылку, нажми "🔗 Моя реферальная ссылка".  

💔 **Что делать, если у друга нет юзернейма?**  
В этом случае остается только **использовать реферальную ссылку**.
            """, parse_mode="Markdown")

            await message.answer("""
            💡 **Полезные советы**  

✨ Размещай свою **реферальную ссылку** в профиле, в своем **ТГК** или просто **делись с друзьями**!  
✨ Если ты отправил валентинку, но получатель **не зашел в бота**, **напиши в предложку канала "[В Макситете Любят](https://t.me/anonaskbot?start=Maxitet)"** со ссылкой на пользователя** — мы вежливо и **анонимно** напомним заглянуть!
            """, parse_mode="Markdown")

            for key in valentine_keys:
                if isinstance(key, tuple):
                    key = key[0]

                user_from_name, valentine_text, user_from_id = get_valentine_by_key(key)

                await message.answer(f"💌 Тебе отправили валентинку!\nОт: {user_from_name[0]}\nНадпись на валентинке: {valentine_text[0]}", parse_mode="Markdown")
                add_counter_get(user_id)
                add_counter_sent(user_from_id[0])
                set_state_valentine_delivered(key)

        await message.answer("❣️ Выбери действие: ❣️", parse_mode="Markdown", reply_markup=menu_keyboard())
        return await menu_router.message.trigger(message)


#==========================================================================================================================================
# Обработка кнопок главного меню

@menu_router.message(F.text == "🔗 Моя реферальная ссылка")
async def get_ref(message: types.Message):
    user_id = message.from_user.id
    user_ref = get_user_ref(user_id)
    await message.answer(f"""🔗 Твоя реферальная ссылка:  
https://t.me/{BOT_USERNAME}?start={user_ref}

💘 Отправь немного любви! 💘""")
    await message.answer("❣️ Выбери действие: ❣️", reply_markup=menu_keyboard())

@menu_router.message(F.text == "📈 Моя статистика")
async def user_stats(message: types.Message):
    user_id = message.from_user.id
    sent_count, get_count = get_user_stats(user_id)

    await message.answer(f"""
    📊 **Твоя статистика**  
💌 Получено валентинок: **{get_count}**  
📨 Отправлено валентинок: **{sent_count}**""", parse_mode="Markdown")
    await message.answer("❣️ Выбери действие: ❣️", parse_mode="Markdown", reply_markup=menu_keyboard())

@menu_router.message(F.text == "💌 Отправить валентинку")
async def send_valentine(message: types.Message, state: FSMContext):
    await message.answer("""💌 **Чтобы отправить валентинку, укажи юзернейм получателя (начинается с @).**  
📩 **Введите юзернейм адресата:**
""", parse_mode="Markdown")
    await state.set_state(StatesValentine.waiting_for_username)
    return await valentine_create.message.trigger(message)

#==========================================================================================================================================
# Отправка валентинки из меню

@valentine_create.message(StatesValentine.waiting_for_username)
async def get_valentine_username_to(message: types.Message, state: FSMContext):
    username = message.text.replace("@", "")
    username = username.replace(" ", '')
    user_from_id = message.from_user.id
    if username == message.from_user.username:
        await message.answer("😔 Ой-ой! Ты слишком чудесен, но нельзя послать себе валентинку! 💌✨")
    else:
        await state.update_data(user_from_id=user_from_id)
        await state.update_data(user_name_to=username)
        user_in_db, user_id_for = check_user_id_db(username)
        if user_in_db:
            await message.answer("""✅ Пользователь найден в базе!  
💖 Он получит валентинку **моментально**!""", parse_mode="Markdown")
            await state.update_data(user_in_db=True)
            await state.update_data(user_id_to=user_id_for)
        else:
            await message.answer("""⚠️ **Внимание!**  
🚀 **Получатель ещё не запускал бота.**  
Как только он **активирует бота**, валентинка будет доставлена автоматически!  

💡 Если ты **стесняешься** попросить его запустить бота, **напиши в предложку канала "[В Макситете Любят](https://t.me/anonaskbot?start=Maxitet)"** — мы передадим просьбу **анонимно!** 😊""", parse_mode="Markdown")
            await state.update_data(user_in_db=False)
            await state.update_data(user_id_to=None)

        kb = [
            [types.KeyboardButton(text="📜 Автозаполнение")]
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
    if valentine_text == "📜 Автозаполнение":
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
    await message.answer("""
    💌 Готово! Теперь выбери, как отправить валентинку:
Хочешь, чтобы получатель знал, от кого она, или оставить интригу и отправить анонимно? 😉✨
💖 Нажми на кнопку или введи собсвтвенный вариант!""", reply_markup=keyboard)
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
        await message.answer(f"""💝 Вот как будет выглядеть твоя валентинка:  

👤От: {user_from}
📬Кому: @{user_to}
🏷Надпись на валентинке: {valentine_text}""" ,reply_markup=change_text_btn("change_valentine_text"))
    else:
        await message.answer(f"""💝 Вот как будет выглядеть твоя валентинка:  

        👤От: {user_from}
        📬Кому: @{user_to}
        🏷Надпись на валентинке: {valentine_text}""")

    await message.answer("Подтвердить отправку валентинки?", reply_markup=y_n_keyboard())
    await state.set_state(StatesValentine.waiting_for_accept)


@valentine_create.message(StatesValentine.waiting_for_accept)
async def y_or_n_send_valentine(message: types.Message, state: FSMContext):
    # print("Нажата кнопка")
    text = message.text

    if text == "Да!":
        valentine_data = await state.get_data()
        #print(valentine_data)
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
            await bot.send_message(chat_id=user_id_for, text=f" 💝Тебе отправили валентинку!\n👤От: {user_from_name}\n🏷Надпись на валентинке: {valentine_text}")
            add_counter_get(user_id_for)
            send_valentine_to_db(user_from_id, user_to, valentine_text, anonimous, send_momental, user_from_name, user_id_for)
            await message.answer("💌 Валентинка доставлена!✅", reply_markup=menu_keyboard())
        else:
            send_valentine_to_db(user_from_id, user_to, valentine_text, anonimous, send_momental, user_from_name, user_id_for)
            await message.answer("💌 Валентинка сохранена! \n✅Пользователь получит ее при первой активации бота!", reply_markup=menu_keyboard())

        await state.clear()
        return await menu_router.message.trigger(message)


    elif text == "Нет!":
        await message.answer("🚨 Отправка валентинки прервана!", reply_markup=menu_keyboard())
        await state.clear()
        return await menu_router.message.trigger(message)

    else:
        await message.answer("Введите ✅Да или ⛔️Нет!")

#==========================================================================================================================================
# Отправка валентинки по реферальной ссылке

@ref_valentine_create.message(StatesValentineRef.waiting_for_valentine_text)
async def ref_valentine_text(message: types.Message, state: FSMContext):
    text = message.text

    if text == "📜 Автозаполнение":
        await state.update_data(valentine_text="generate_auto")
    else:
        await state.update_data(valentine_text=text)

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
    # print(valentine_data)
    user_to = valentine_data['ref_user_id']
    valentine_text = valentine_data['valentine_text']
    user_from = valentine_data['user_name_from']

    if valentine_text == "generate_auto":
        valentine_text = valentine_random_text[r.randint(0, len(valentine_random_text)-1)]
        await state.update_data(valentine_text=valentine_text)
        await message.answer(f"""💝 Вот как будет выглядеть твоя валентинка:  

👤От: {user_from}
🏷Надпись на валентинке: {valentine_text}""""", reply_markup=change_text_btn("ref_change_valentine_text"))
    else:
        await message.answer(f"""💝 Вот как будет выглядеть твоя валентинка:  

👤От: {user_from}
🏷Надпись на валентинке: {valentine_text}""")

    await message.answer("Подтвердить отправку валентинки?", reply_markup=y_n_keyboard())
    await state.set_state(StatesValentineRef.waiting_for_accept)

@ref_valentine_create.message(StatesValentineRef.waiting_for_accept)
async def y_or_n_send_valentine(message: types.Message, state: FSMContext):
    text = message.text

    if text == "Да!":
        valentine_data = await state.get_data()
        print(valentine_data)
        valentine_text = valentine_data['valentine_text']
        user_from = valentine_data['user_name_from']
        user_id_for = valentine_data['ref_user_id']
        user_to = valentine_data['ref_user_id']
        user_id_from = message.from_user.id

        if user_from == "anonimous":
            anonimous = True
        else:
            anonimous = False

        if isinstance(user_id_for, tuple):
            user_id_for = user_id_for[0]


        await bot.send_message(chat_id=user_id_for, text=f" 💝Тебе отправили валентинку!\n👤От: {user_from}\n🏷Надпись на валентинке: {valentine_text}")
        add_counter_get(user_id_for)
        add_counter_sent(user_id_from)
        send_valentine_to_db(user_from, user_to, valentine_text, anonimous, True, user_from, user_id_for)
        await message.answer("💌 Валентинка доставлена!✅", reply_markup=menu_keyboard())
        await state.clear()
        return await menu_router.message.trigger(message)

    elif text == "Нет!":
        await message.answer("🚨 Отправка валентинки прервана!", reply_markup=menu_keyboard())
        await state.clear()
        return await menu_router.message.trigger(message)
    else:
        await message.answer("Введите ✅Да или ⛔️Нет!")

#==========================================================================================================================================
# Обработки инлайн кнопок

@dp.callback_query(F.data == "change_valentine_text")
async def change_valentine_text(call: types.CallbackQuery, state: FSMContext):

    valentine_data = await state.get_data()
    user_to = valentine_data['user_name_to']
    user_from = valentine_data['user_from_name']

    valentine_text = valentine_random_text[r.randint(0, len(valentine_random_text)-1)]
    await state.update_data(valentine_text=valentine_text)

    await call.message.edit_text(f"Твоя валентинка будет выглядеть так:\nОт: {user_from}\nКому: @{user_to}\nНадпись на валентинке: {valentine_text}", reply_markup=change_text_btn("change_valentine_text"))
    await call.answer()

@dp.callback_query(F.data == "ref_change_valentine_text")
async def change_valentine_text(call: types.CallbackQuery, state: FSMContext):

    valentine_data = await state.get_data()
    user_to = valentine_data['user_name_to']
    user_to = valentine_data['user_name_to']
    user_from = valentine_data['user_from_name']

    valentine_text = valentine_random_text[r.randint(0, len(valentine_random_text)-1)]
    await state.update_data(valentine_text=valentine_text)

    await call.message.edit_text(f"Твоя валентинка будет выглядеть так:\nОт: {user_from}\nКому: @{user_to}\nНадпись на валентинке: {valentine_text}", reply_markup=change_text_btn("ref_change_valentine_text"))
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
