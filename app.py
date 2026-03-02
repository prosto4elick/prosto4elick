import asyncio
import logging
import os
import random
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiohttp import web

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# --- НАСТРОЙКИ (ID и ТОКЕН) ---
TOKEN = "8654293589:AAHJfddZqbsxQ3iABh-Ebn4_A4415iRaIcI"
CHANNEL_ID = -1001926184793  # Твой основной КАНАЛ
CHAT_ID = -1001942710548     # Твой ЧАТ (Группа)

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
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"✅ Веб-сервер запущен на порту {port}")

# --- УПРАВЛЕНИЕ ИЗ КОНСОЛИ (ДЛЯ ПК) ---
async def terminal_input_listener():
    """Позволяет писать в чат или канал прямо из терминала PyCharm"""
    await asyncio.sleep(2)
    print("\n⌨️  [КОНСОЛЬ] Доступные команды:")
    print("👉 /channel текст — отправить в канал")
    print("👉 /chat текст — отправить в чат")
    print("👉 просто текст — отправить в канал по умолчанию\n")

    while True:
        # Читаем ввод из консоли без блокировки бота
        line = await asyncio.to_thread(sys.stdin.readline)
        text = line.strip()

        if text:
            if text.startswith("/chat"):
                target_id = CHAT_ID
                msg_text = text.replace("/chat", "", 1).strip()
                label = "ЧАТ 💬"
            elif text.startswith("/channel"):
                target_id = CHANNEL_ID
                msg_text = text.replace("/channel", "", 1).strip()
                label = "КАНАЛ 📢"
            else:
                target_id = CHANNEL_ID
                msg_text = text
                label = "КАНАЛ (default) 📢"

            if not msg_text:
                print("⚠️ Ошибка: Пустое сообщение. Введи текст после команды.")
                continue

            try:
                await bot.send_message(chat_id=target_id, text=msg_text)
                print(f"✅ [{label}] Отправлено: {msg_text}")
            except Exception as e:
                print(f"❌ Ошибка отправки: {e}. Проверь права админа у бота!")

# --- КНОПКИ (КЛАВИАТУРЫ) ---
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

# --- КОМАНДЫ В TELEGRAM ---
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

# --- МОДЕРАЦИЯ И ПРИВЕТСТВИЕ ---
@dp.message(F.new_chat_members)
async def welcome_and_clean(message: Message):
    await message.delete() # Удаляем системное сообщение
    for new_user in message.new_chat_members:
        await message.answer(
            f"Йо, {new_user.full_name}! 👋\n\nДобро пожаловать в **4444**! Цены тут: /price 👇",
            reply_markup=keyboard, parse_mode="Markdown"
        )

@dp.message(F.left_chat_member)
async def clean_left_member(message: Message):
    await message.delete() # Удаляем системное сообщение о выходе

# --- АВТО-ОТВЕТЫ ПРИ ПЕРЕСЫЛКЕ ИЗ КАНАЛА ---
@dp.message(F.forward_from_chat.id == CHANNEL_ID)
async def auto_reply_with_photo(message: Message):
    try:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        photo_path = os.path.join(current_dir, "image.png")
        if os.path.exists(photo_path):
            await message.reply_photo(photo=FSInputFile(photo_path),
                                      caption="👇 **Полезные ссылки и прайс:**",
                                      reply_markup=keyboard)
        else:
            await message.reply("Салют! Залетай к нам 🙃", reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Ошибка авто-ответа: {e}")

# --- ЗАПУСК ---
async def main():
    logging.info("🚀 Бот запускается...")
    # Очищаем очередь обновлений
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем всё вместе
    await asyncio.gather(
        start_web_server(),      # Сервер для Render
        dp.start_polling(bot),   # Сам бот (Telegram)
        terminal_input_listener() # Консоль (ПК)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен")
