import os
from maxbot.bot import Bot
from maxbot.dispatcher import Dispatcher
from maxbot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

# Токен берётся из переменной окружения на Bothost
BOT_TOKEN = os.getenv("BOT_TOKEN")

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

# ВАЖНО: @dp.bot_started БЕЗ скобок
@dp.bot_started
async def on_bot_started(update):
    """Срабатывает при нажатии кнопки 'Начать' в MAX"""
    await bot.send_message(
        chat_id=update.user.id,
        text="Привет! Чтобы пользоваться ботом, подпишись на наш канал, а затем нажми кнопку «Я подписался».",
        reply_markup=check_sub_kb
    )

@dp.message()
async def on_message(message: Message):
    """Срабатывает на любое текстовое сообщение"""
    await bot.send_message(
        chat_id=message.sender.id,
        text="Нажми кнопку ниже, чтобы начать.",
        reply_markup=check_sub_kb
    )

@dp.callback()
async def on_callback(cb):
    """Срабатывает на нажатие инлайн-кнопок"""
    
    if cb.payload == "check_sub":
        await bot.send_message(
            chat_id=cb.user.id,
            text="Спасибо! Теперь тебе доступно меню:",
            reply_markup=main_menu_kb
        )
    
    elif cb.payload == "faq_menu":
        await bot.send_message(
            chat_id=cb.user.id,
            text="Выбери вопрос, который тебя интересует:",
            reply_markup=faq_kb
        )
    
    elif cb.payload.startswith("faq_"):
        question = cb.payload[4:]
        answer = FAQ_DATA.get(question, "Извини, не знаю ответа на этот вопрос.")
        await bot.send_message(chat_id=cb.user.id, text=answer)
    
    elif cb.payload == "back_to_menu":
        await bot.send_message(
            chat_id=cb.user.id,
            text="Ты вернулся в главное меню:",
            reply_markup=main_menu_kb
        )

# --- ЗАПУСК (единственный правильный способ для umaxbot) ---
if __name__ == "__main__":
    dp.run_polling()
