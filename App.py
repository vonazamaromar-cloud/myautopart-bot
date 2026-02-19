import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request, abort

TOKEN = os.environ.get('BOT_TOKEN')          # ← сюда токен попадёт через настройки Render
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')  # ← сюда попадёт https://твой-бот.onrender.com

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

WEBHOOK_PATH = f'/{TOKEN}'   # секретный путь, чтобы никто не догадался

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
    markup.add(InlineKeyboardButton("← Вернуться в бот", url=f"https://t.me/{bot.get_me().username}"))

    bot.reply_to(message,
                 f"✅ VIN принят: <code>{vin}</code>\n\n"
                 "Перейди в каталог, посмотри запчасти.\n"
                 "Потом вернись и напиши артикул — помогу заказать!",
                 reply_markup=markup,
                 parse_mode='HTML')

    bot.reply_to(message, "Жду артикул 👇")

@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    else:
        abort(403)

if __name__ == '__main__':
    # Это только для локального теста, на Render не используется
    pass
