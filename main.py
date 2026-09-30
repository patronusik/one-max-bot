import os
import asyncio
from maxbot.bot import Bot
from maxbot.dispatcher import Dispatcher
from maxbot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("MAX_BOT_TOKEN") or os.getenv("MAX_TOKEN")

# Для отладки — покажет первые 10 символов токена или "НЕ НАЙДЕН"
print(f"TOKEN: {BOT_TOKEN[:10] if BOT_TOKEN else 'НЕ НАЙДЕН'}...")

if not BOT_TOKEN:
    raise SystemExit("❌ Токен не найден. Проверьте переменные окружения MAX_BOT_TOKEN / MAX_TOKEN")

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)

# --- НАСТРОЙКИ ---
CHANNEL_URL = "https://max.ru/твой_канал"
SITE_URL = "https://example.com"

# --- FAQ ---
FAQ_DATA = {
    "Как заказать?": "Чтобы заказать, напиши нам на почту example@mail.ru или позвони по телефону +7 (999) 123-45-67.",
    "Сколько стоит?": "Актуальные цены указаны на нашем сайте: " + SITE_URL,
    "Как оплатить?": "Оплатить можно картой или переводом. Реквизиты пришлём после оформления заказа.",
    "Есть ли доставка?": "Да, доставка по всей России. Сроки: 1-3 дня."
}

# --- КЛАВИАТУРЫ ---
check_sub_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📢 Подписаться на канал", url=CHANNEL_URL)],
    [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_sub")]
])

main_menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🌐 Официальный сайт", url=SITE_URL)],
    [InlineKeyboardButton(text="❓ Частые вопросы (FAQ)", callback_data="faq_menu")]
])

faq_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Как заказать?", callback_data="faq_Как заказать?")],
    [InlineKeyboardButton(text="Сколько стоит?", callback_data="faq_Сколько стоит?")],
    [InlineKeyboardButton(text="Как оплатить?", callback_data="faq_Как оплатить?")],
    [InlineKeyboardButton(text="Есть ли доставка?", callback_data="faq_Есть ли доставка?")],
    [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu")]
])

# --- ОБРАБОТЧИКИ ---

@dp.bot_started
async def on_bot_started(update):
    """Срабатывает при нажатии кнопки 'Начать' в MAX"""
    user_id = update['user']['user_id']
    print(f"BOT_STARTED: user_id={user_id}")
    await bot.send_message(
        user_id=user_id,
        text="Привет! Чтобы пользоваться ботом, подпишись на наш канал, а затем нажми кнопку «Я подписался».",
        reply_markup=check_sub_kb
    )

@dp.message()
async def on_message(message: Message):
    """Срабатывает на любое текстовое сообщение"""
    print(f"MESSAGE: text={getattr(message, 'text', None)} sender={message.sender.id}")
    await bot.send_message(
        user_id=message.sender.id,
        text="Нажми кнопку ниже, чтобы начать.",
        reply_markup=check_sub_kb
    )

@dp.callback()
async def on_callback(cb):
    """Срабатывает на нажатие инлайн-кнопок"""
    print(f"CALLBACK: payload={cb.payload} user={getattr(cb, 'user', None)}")

    # Пытаемся получить user_id разными способами — зависит от версии umaxbot
    user_id = None
    if hasattr(cb, "user") and cb.user is not None:
        user_id = getattr(cb.user, "id", None) or (cb.user.get("user_id") if isinstance(cb.user, dict) else None)

    if user_id is None:
        # запасной вариант: иногда user_id лежит прямо в cb
        user_id = getattr(cb, "user_id", None)

    print(f"CALLBACK: resolved user_id={user_id}")

    if cb.payload == "check_sub":
        await bot.send_message(
            user_id=user_id,
            text="Спасибо! Теперь тебе доступно меню:",
            reply_markup=main_menu_kb
        )

    elif cb.payload == "faq_menu":
        await bot.send_message(
            user_id=user_id,
            text="Выбери вопрос, который тебя интересует:",
            reply_markup=faq_kb
        )

    elif cb.payload.startswith("faq_"):
        question = cb.payload[4:]
        answer = FAQ_DATA.get(question, "Извини, не знаю ответа на этот вопрос.")
        await bot.send_message(user_id=user_id, text=answer)

    elif cb.payload == "back_to_menu":
        await bot.send_message(
            user_id=user_id,
            text="Ты вернулся в главное меню:",
            reply_markup=main_menu_kb
        )

# --- ЗАПУСК ---
if __name__ == "__main__":
    asyncio.run(dp.run_polling())
