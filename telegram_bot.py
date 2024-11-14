import logging
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
import pickle
import numpy as np
import string
from util.parser import JSONParser
from dotenv import load_dotenv

load_dotenv()

def preprocess(chat):
    chat = chat.lower()
    tandabaca = tuple(string.punctuation)
    chat = ''.join(ch for ch in chat if ch not in tandabaca)
    return chat

def bot_response(chat, pipeline, jp):
    chat = preprocess(chat)
    res = pipeline.predict_proba([chat])
    max_prob = max(res[0])
    if max_prob < 0.065:
        return "🙏 *Maaf, saya tidak dapat memberikan jawaban untuk pertanyaan tersebut.*\n\nNamun, jika Anda membutuhkan informasi lebih lanjut atau memiliki pertanyaan yang lebih spesifik, silahkan coba ketik ulang dengan lebih detail atau menghubungi *Humas UIB*.\n\nTim Humas kami siap memberikan penjelasan yang lebih mendalam dan menjawab pertanyaan Anda yang lebih detail.", None
    else:
        max_id = np.argmax(res[0])
        pred_tag = pipeline.classes_[max_id]
        response = jp.get_response(pred_tag)
        return response, pred_tag

with open("model_chatbot.pkl", "rb") as model_file:
    pipeline = pickle.load(model_file)

jp = JSONParser()
jp.parse("data/intents.json")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Function to get a random pattern from subintents
def get_random_pattern(jp):
    patterns = []
    for intent in jp.data['intents']:
        if 'subintents' in intent:
            for subintent in intent['subintents']:
                patterns.extend(subintent['patterns'])
    return random.choice(patterns)

# Function to create inline keyboard
def create_inline_keyboard(pattern):
    keyboard = [
        [InlineKeyboardButton("Tanya", callback_data=pattern[:64]), InlineKeyboardButton("Minta Pertanyaan Lain", callback_data="minta_pertanyaan_lain")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('*Hi!* Anda sedang terhubung dengan chatbot kami yang saat ini masih dalam tahap pengembangan. 😊\n\nKami sedang bekerja keras untuk meningkatkan kemampuan chatbot ini agar dapat memberikan informasi yang lebih lengkap dan akurat. Saat ini, chatbot ini bisa memberikan jawaban terbatas, namun tim kami selalu siap membantu jika Anda membutuhkan informasi lebih lanjut.\n\nTerima kasih atas kesabaran Anda, dan kami akan terus berusaha memberikan pengalaman yang lebih baik!', parse_mode='Markdown')

async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("*Untuk memulai percakapan, ketik /start.*\n\nSetelah Anda siap, ketik perintah tersebut untuk mengakses layanan kami.\n\n*Untuk rekomendasi pertanyaan, ketik /tanya.* Gunakan perintah ini untuk mendapatkan rekomendasi pertanyaan dari chatbot kami.\n\n*Untuk mengakhiri chat, ketik 'bye'.* Jika Anda sudah selesai atau ingin berhenti, cukup ketik 'bye' dan percakapan akan berakhir. Kami siap membantu kapan saja!", parse_mode='Markdown')

async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    response, tag = bot_response(user_message, pipeline, jp)
    await update.message.reply_text(response, parse_mode='Markdown')
    if tag == 'bye' or tag == 'bye_umum':
        await update.message.reply_text('*Sampai jumpa!* 👋\n\nTerima kasih banyak telah menjadi bagian dari pengujian chatbot kami. 🙏 Kami sangat menghargai waktu dan masukan Anda yang sangat berharga.', parse_mode='Markdown')

async def random_pattern_command(update: Update, context: CallbackContext) -> None:
    pattern = get_random_pattern(jp)
    keyboard = create_inline_keyboard(pattern)
    await update.message.reply_text(f"✨ *Rekomendasi Pertanyaan* ✨\nBerikut adalah pertanyaan yang mungkin membantu Anda:\n\n**{pattern}**", reply_markup=keyboard, parse_mode='Markdown')

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_message = query.data

    if user_message == "minta_pertanyaan_lain":
        pattern = get_random_pattern(jp)
        keyboard = create_inline_keyboard(pattern)
        await query.edit_message_text(f"✨ *Rekomendasi Pertanyaan* ✨\nBerikut adalah pertanyaan baru yang mungkin lebih bagus dari sebelumnya:\n\n**{pattern}**", reply_markup=keyboard, parse_mode='Markdown')
    else:
        response, tag = bot_response(user_message, pipeline, jp)
        await query.edit_message_text(f"Anda: {user_message}", parse_mode='Markdown')
        await query.message.reply_text(response, parse_mode='Markdown')

def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("Tidak ada token yang ditemukan di environment variable TELEGRAM_BOT_TOKEN")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("tanya", random_pattern_command))
    application.add_handler(CallbackQueryHandler(button))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()