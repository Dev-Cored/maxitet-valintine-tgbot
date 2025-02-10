import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import sqlite3
import hashlib

import database
from database import *

logging.basicConfig(level=logging.INFO)

database.init_db()

BOT_USERNAME = "maxitet_family_valentines_bot"
def gen_ref_url(user_id):
    ref_code = hashlib.md5(str(user_id).encode()).hexdigest()[:8]
    return f"https://t.me/{BOT_USERNAME}?start=ref_{ref_code}"


with open('token.txt') as f:
    TOKEN = f.read().strip()

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def start_command(message: types.Message):
    # Получаем текст сообщения и разделяем его по пробелам
    args = message.text.split()

    if len(args) > 1:
        ref_code = args[1]
        await message.answer(f"🔗 Вы перешли по реферальной ссылке! Код: {ref_code}")
    else:
        await message.answer("👋 Привет! У вас нет реферального кода.")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
