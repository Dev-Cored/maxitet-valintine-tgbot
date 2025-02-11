import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import Router, F
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


with open('token.txt') as f:
    TOKEN = f.read().strip()

bot = Bot(token=TOKEN)
dp = Dispatcher()

menu_router = Router()
valentine_create = Router()
ref_valentine_create = Router()
reg_user = Router()



@dp.message(Command('start'))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    ref_url = gen_ref_url(user_id)

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
        kb = [
            [types.KeyboardButton(text="💌 Отправить валентинку")],
            [types.KeyboardButton(text="🔗 Моя реферальная ссылка"),
             types.KeyboardButton(text="📈 Моя статистика")]
        ]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            input_field_placeholder="Выберите действие")
        await message.answer("Что вы хотите сделать?", reply_markup=keyboard)
        return await menu_router.message.trigger(message)

@menu_router.message(F.text == "🔗 Моя реферальная ссылка")
async def get_ref(message: types.Message):
    user_id = message.from_user.id
    user_ref = get_user_ref(user_id)
    await message.answer("Твоя реферальная ссылка: \nhttps://t.me/{BOT_USERNAME}?start={ref_code}")

@menu_router.message(F.Text == "💌 Отправить валентинку")
async def send_valentine(message: types.Message):
    a = 1



async def main():
    await dp.start_polling(bot)
    await dp.include_router(menu_router)


if __name__ == "__main__":
    asyncio.run(main())
