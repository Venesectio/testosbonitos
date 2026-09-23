import asyncio
import logging
import json

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
)

# ==== Настройки ====
BOT_TOKEN = "ВАШ_ТОКЕН_БОТА"          # получить у @BotFather
WEBAPP_URL = "https://ваш-домен.tld/webapp/index.html"  # HTTPS-адрес index.html

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def get_webapp_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой, открывающей Mini App."""
    button = KeyboardButton(
        text="💣 Играть в Сапёр",
        web_app=WebAppInfo(url=WEBAPP_URL),
    )
    return ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True)


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Нажми на кнопку ниже, чтобы открыть игру «Сапёр» "
        "прямо внутри Telegram.",
        reply_markup=get_webapp_keyboard(),
    )


@dp.message(F.web_app_data)
async def on_webapp_data(message: Message):
    """
    Сюда приходят данные из Mini App, отправленные через
    Telegram.WebApp.sendData(...) в index.html.
    Работает только для кнопок, открытых через ReplyKeyboard (как выше),
    не через inline-кнопки.
    """
    try:
        data = json.loads(message.web_app_data.data)
    except (ValueError, AttributeError):
        await message.answer("Не удалось прочитать данные из игры.")
        return

    if data.get("event") == "game_finished":
        won = data.get("won")
        time_spent = data.get("time")
        level = data.get("level", "easy")
        if won:
            text = f"🎉 Ты выиграл на уровне «{level}»! Время: {time_spent} сек."
        else:
            text = f"💥 Взорвался на уровне «{level}». Время: {time_spent} сек. Попробуй ещё раз!"
        await message.answer(text, reply_markup=get_webapp_keyboard())


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
