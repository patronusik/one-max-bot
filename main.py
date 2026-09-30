import os
import asyncio
from maxbot.bot import Bot
from maxbot.dispatcher import Dispatcher
from maxbot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

# Токен будет браться из переменной окружения на Bothost
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)

# --- НАСТРОЙКИ (поменяй под себя) ---
CHANNEL_URL = "https://max.ru/твой_канал"  # Ссылка на твой канал
SITE_URL = "https://example.com"            # Ссылка на официальный сайт

# --- FAQ (вопрос-ответ) ---
FAQ_DATA = {
    "Как заказать?": "Чтобы заказать, напиши нам на почту example@mail.ru или позвони по телефону +7 (999) 123-45-67.",
    "Сколько стоит?": "Актуальные цены указаны на нашем сайте: " + SITE_URL,
    "Как оплатить?": "Оплатить можно картой или переводом. Реквизиты пришлём после оформления заказа.",
    "Есть ли доставка?": "Да, доставка по всей России. Сроки: 1-3 дня."
}

# --- КЛАВИАТУРЫ ---
# Кнопка проверки подписки
check_sub_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📢 Подписаться на канал", url=CHANNEL_URL)],
    [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_sub")]
])

# Главное меню
main_menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🌐 Официальный сайт", url=SITE_URL)],
    [InlineKeyboardButton(text="❓ Частые вопросы (FAQ)", callback_data="faq_menu")]
])

# Меню FAQ
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
    """Срабатывает, когда пользователь нажимает кнопку 'Начать' в MAX"""
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
    
    # Пользователь нажал "Я подписался" -> показываем главное меню
    if cb.payload == "check_sub":
        await bot.send_message(
            chat_id=cb.user.id,
            text="Спасибо! Теперь тебе доступно меню:",
            reply_markup=main_menu_kb
        )
    
    # Пользователь нажал "FAQ" -> показываем список вопросов
    elif cb.payload == "faq_menu":
        await bot.send_message(
            chat_id=cb.user.id,
            text="Выбери вопрос, который тебя интересует:",
            reply_markup=faq_kb
        )
    
    # Пользователь нажал один из вопросов FAQ
    elif cb.payload.startswith("faq_"):
        # Вырезаем сам вопрос из payload (убираем "faq_")
        question = cb.payload[4:]
        answer = FAQ_DATA.get(question, "Извини, не знаю ответа на этот вопрос.")
        await bot.send_message(chat_id=cb.user.id, text=answer)
    
    # Пользователь нажал "Назад в меню"
    elif cb.payload == "back_to_menu":
        await bot.send_message(
            chat_id=cb.user.id,
            text="Ты вернулся в главное меню:",
            reply_markup=main_menu_kb
        )

# --- ЗАПУСК ---
async def main():
    # Удаляем старые webhook-подписки, чтобы polling работал
    try:
        await bot.delete_webhook()
        print("Webhook удалён")
    except Exception as e:
        print(f"Webhook cleanup: {e}")
    
    # Запускаем polling
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
