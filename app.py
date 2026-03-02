import asyncio
import logging
import os
import random
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiohttp import web  # Важно для анти-сна

# Настройка логирования
logging.basicConfig(level=logging.INFO)

TOKEN = "8654293589:AAHJfddZqbsxQ3iABh-Ebn4_A4415iRaIcI"
CHANNEL_ID = -1001926184793

bot = Bot(token=TOKEN)
dp = Dispatcher()


# --- ВЕБ-СЕРВЕР ДЛЯ RENDER (АНТИ-СОН) ---
async def handle(request):
    return web.Response(text="Bot is alive!")


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render передает порт в переменную окружения PORT
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Веб-сервер запущен на порту {port}")


# --- Кнопки ---
keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Вступить в чат 💬", url="https://t.me/+efp0EWYXe-1kNDIy")],
    [InlineKeyboardButton(text="TikTok 📱", url="https://www.tiktok.com/@prosto4444elick?_r=1&_t=ZT-94KidViIjYE")],
    [InlineKeyboardButton(text="Каталог битов BeatChain 🎵",
                          url="https://t.me/beatchainbot/beatchain?startapp=profile5025272062")]
])

price_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Купить бит в боте 🛒",
                          url="https://t.me/beatchainbot/beatchain?startapp=profile5025272062")],
    [InlineKeyboardButton(text="Написать в ЛС 📩", url="https://t.me/prosto4elick")]
])


# --- Команды ---
@dp.message(Command("price"))
async def cmd_price(message: Message):
    price_text = (
        "💰 **price:**\n\n"
        "🔹 **MP3** - 444₽\n"
        "🔹 **WAV** - 1444₽\n"
        "🔹 **TRACKOUT** - 2444₽\n"
        "🔹 **EXCLUSIVE** - 2444₽\n\n"
        "ЛС - @prosto4elick"
    )
    await message.answer(price_text, reply_markup=price_keyboard, parse_mode="Markdown")


@dp.message(Command("rate"))
async def cmd_rate(message: Message, command: CommandObject):
    if command.args:
        try:
            args = command.args.split()
            start, end = int(args[0]), int(args[1])
            if start > end: start, end = end, start
            number = random.randint(start, end)
            await message.reply(f"🎲 Рандом выдал: **{number}**", parse_mode="Markdown")
        except (ValueError, IndexError):
            await message.reply("❌ Пиши числа через пробел: `/rate 1 100`")
    else:
        number = random.randint(1, 10)
        await message.reply(f"🎲 Твоя оценка: **{number}/10**")


@dp.message(Command("links"))
async def send_links_command(message: Message):
    await message.reply("🔗 **Все важные ссылки:**", reply_markup=keyboard, parse_mode="Markdown")


# --- Модерация чата ---
@dp.message(F.new_chat_members)
async def welcome_and_clean(message: Message):
    await message.delete()
    for new_user in message.new_chat_members:
        await message.answer(
            f"Йо, {new_user.full_name}! 👋\n\nДобро пожаловать в **4444**! Цены тут: /price 👇",
            reply_markup=keyboard, parse_mode="Markdown"
        )


@dp.message(F.left_chat_member)
async def clean_left_member(message: Message):
    await message.delete()


# --- Авто-комменты ---
@dp.message(F.forward_from_chat.id == CHANNEL_ID)
async def auto_reply_with_photo(message: Message):
    try:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        photo_path = os.path.join(current_dir, "image.png")
        if os.path.exists(photo_path):
            await message.reply_photo(photo=FSInputFile(photo_path), caption="👇 **Полезные ссылки и прайс:**",
                                      reply_markup=keyboard)
        else:
            await message.reply("👇 **Полезные ссылки:**", reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Ошибка: {e}")


# --- ГЛАВНЫЙ ЗАПУСК ---
async def main():
    logging.info("🚀 Запуск бота...")

    # Удаляем вебхуки, если они были (на всякий случай)
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем веб-сервер и бота параллельно
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен")