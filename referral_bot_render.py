# Бот на Python з реферальною системою для Telegram
# Працює через aiogram (асинхронна бібліотека)
# Готовий до розгортання на Render або Railway

from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
import logging
import os
from collections import defaultdict

# Встав свій токен від @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN") or "ВСТАВ_СВІЙ_ТОКЕН"
CHANNEL_ID = os.getenv("CHANNEL_ID") or "@назва_каналу"

# Просте зберігання рефералів у пам'яті (на проді — база)
referrals = defaultdict(list)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Перевірка, чи користувач підписаний на канал
async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "creator", "administrator"]
    except Exception:
        return False

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    args = message.get_args()
    user_id = message.from_user.id

    # Якщо є реферальний код
    if args and args != str(user_id):
        if user_id not in referrals[args]:
            referrals[args].append(user_id)

    sub = await is_subscribed(user_id)
    if sub:
        await message.answer("Дякую за підписку! 🎉")
    else:
        await message.answer(f"Щоб взяти участь — підпишись на канал {CHANNEL_ID}, а потім натисни /start")

    await message.answer(f"Твоє реферальне посилання:
https://t.me/{(await bot.get_me()).username}?start={user_id}")

@dp.message_handler(commands=['stats'])
async def stats_handler(message: types.Message):
    user_id = str(message.from_user.id)
    count = len(referrals[user_id])
    await message.answer(f"Ти запросив: {count} людей")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
