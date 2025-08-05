# bot.py
import logging
import os
from collections import defaultdict

from aiogram import Bot, Dispatcher, executor, types

BOT_TOKEN = os.getenv("BOT_TOKEN") or "ВСТАВ_СВІЙ_ТОКЕН"
CHANNEL_ID = os.getenv("CHANNEL_ID") or "@назва_каналу"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Зберігаємо рефералів у пам'яті (для продакшн краще БД)
referrals = defaultdict(list)

async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "creator", "administrator"]
    except Exception:
        return False

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    args = message.get_args()
    user_id = str(message.from_user.id)

    # Якщо є реферальний код і це не власний код
    if args and args != user_id:
        if user_id not in referrals[args]:
            referrals[args].append(user_id)

    sub = await is_subscribed(message.from_user.id)
    if sub:
        await message.answer("Дякую за підписку! 🎉")
    else:
        await message.answer(f"Підпишись на канал {CHANNEL_ID}, щоб брати участь.")

    bot_username = (await bot.get_me()).username
    await message.answer(f"Твоє реферальне посилання:\nhttps://t.me/{bot_username}?start={user_id}")

@dp.message_handler(commands=['stats'])
async def stats_handler(message: types.Message):
    user_id = str(message.from_user.id)
    count = len(referrals[user_id])
    await message.answer(f"Ти запросив: {count} людей")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
