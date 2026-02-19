import os
import logging
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request, abort

# Логирование — очень важно для отладки
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    raise ValueError("BOT_TOKEN not set in environment variables")

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# Простой путь (без токена в пути — безопасно и надёжно)
WEBHOOK_PATH = '/webhook'

# Кэшируем username бота, чтобы не делать лишних запросов
try:
    BOT_USERNAME = bot.get_me().username
    logger.info(f"Bot username: @{BOT_USERNAME}")
except Exception as e:
    logger.error(f"Failed to get bot username: {e}")
    BOT_USERNAME = "MyAutoPart_bot"  # fallback на случай ошибки

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
                 "🚗 Привет! Я AutoPartsBotKRSK\n\n"
                 "Пришли VIN (ровно 17 символов)\n"
                 "Пример: JTEBU5JR0K5641234")

@bot.message_handler(func=lambda m: True)
def handle_vin(message):
    vin = message.text.strip().upper().replace(" ", "").replace("-", "")
    
    if len(vin) != 17:
        bot.reply_to(message, "❌ VIN должен быть ровно 17 символов.")
        return
    
    allowed = set("0123456789ABCDEFGHJKLMNPRSTUVWXYZ")
    if not all(c in allowed for c in vin):
        bot.reply_to(message, "❌ Недопустимые символы (без I, O, Q).")
        return

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("Emex.ru — большой выбор + фото", url=f"https://emex.ru/catalogs?search={vin}"))
    markup.add(InlineKeyboardButton("Autodoc.ru — часто дешевле", url=f"https://www.autodoc.ru/search?query={vin}"))
    markup.add(InlineKeyboardButton("Euroauto.ru — альтернатива", url=f"https://euroauto.ru/search/?q={vin}"))
    markup.add(InlineKeyboardButton("← Вернуться в бот", url=f"https://t.me/{BOT_USERNAME}"))

    bot.reply_to(message,
                 f"✅ VIN принят: <code>{vin}</code>\n\n"
                 "Перейди в каталог, посмотри запчасти.\n"
                 "Потом вернись и напиши артикул — помогу заказать!",
                 reply_markup=markup,
                 parse_mode='HTML')

    bot.reply_to(message, "Жду артикул 👇")

@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    logger.info("Webhook called")  # ← увидим в логах, что запрос пришёл
    if request.headers.get('content-type') == 'application/json':
        try:
            json_string = request.get_data().decode('utf-8')
            update = types.Update.de_json(json_string)
            if update:
                logger.info(f"Processing update from user {update.message.from_user.id if update.message else 'unknown'}")
                bot.process_new_updates([update])
                logger.info("Update processed successfully")
                return 'OK', 200
            else:
                logger.warning("Invalid update received")
                return 'Invalid update', 400
        except Exception as e:
            logger.error(f"Error processing update: {e}", exc_info=True)
            return 'Internal error', 500
    else:
        logger.warning("Non-JSON content type")
        abort(403)

if __name__ == '__main__':
    pass
