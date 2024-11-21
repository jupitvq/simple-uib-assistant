import logging
import os
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
import pickle
import numpy as np
import string
from util.parser import JSONParser
from dotenv import load_dotenv

load_dotenv()

TYPING_DELAY = 1
TYPING_UPDATE_DELAY = 0.5

def preprocess(chat):
    chat = chat.lower()
    tandabaca = tuple(string.punctuation)
    chat = ''.join(ch for ch in chat if ch not in tandabaca)
    return chat

def bot_response(chat, pipeline, jp):
    chat = preprocess(chat)
    res = pipeline.predict_proba([chat])
    max_prob = max(res[0])
    if max_prob < 0.08:
        response = "🙏 *Maaf, saya tidak dapat memberikan jawaban untuk pertanyaan tersebut.*\n\nNamun, jika Anda membutuhkan informasi lebih lanjut atau memiliki pertanyaan yang lebih spesifik, silahkan coba ketik ulang dengan lebih detail atau menghubungi *Humas UIB*.\n\n📱 *LINE Pusat Informasi UIB:* [https://lin.ee/2Ep0bNN](https://lin.ee/2Ep0bNN)\n📞 *WhatsApp Humas UIB:* [0812-7526-2369](https://wa.me/6281275262369)\n\nTim Humas kami siap memberikan penjelasan yang lebih mendalam dan menjawab pertanyaan Anda yang lebih detail."
        logger.info(f"User question: {chat}, max_prob: {max_prob}, tag: None, patterns: None, response: {response}")
        return response, None, None
    elif 0.08 <= max_prob < 0.19:
        max_id = np.argmax(res[0])
        pred_tag = pipeline.classes_[max_id]
        if pred_tag in ['salam', 'bye', 'kemampuan', 'salam_pertanyaan', 'salam_umum', 'bye_umum', 'kemampuan_pertanyaan']:
            response = jp.get_response(pred_tag)
            logger.info(f"User question: {chat}, max_prob: {max_prob}, tag: {pred_tag}, patterns: None, response: {response}")
            return response, None, pred_tag
        subintents = [intent for intent in jp.data['intents'] if any(subintent['tag'] == pred_tag for subintent in intent.get('subintents', []))]
        if subintents:
            subintent = subintents[0]
            other_subintents = [si for si in subintent['subintents'] if si['tag'] != pred_tag]
            if other_subintents:
                other_subintent = random.choice(other_subintents)
                pattern = random.choice(other_subintent['patterns'])
                keyboard = create_inline_keyboard([pattern])
                response = jp.get_response(pred_tag)
                logger.info(f"User question: {chat}, max_prob: {max_prob}, tag: {pred_tag}, patterns: {other_subintent['patterns']}, response: {response}")
                return response, keyboard, pred_tag
    else:
        max_id = np.argmax(res[0])
        pred_tag = pipeline.classes_[max_id]
        response = jp.get_response(pred_tag)
        logger.info(f"User question: {chat}, max_prob: {max_prob}, tag: {pred_tag}, patterns: None, response: {response}")
        return response, None, pred_tag

with open("model_chatbot.pkl", "rb") as model_file:
    pipeline = pickle.load(model_file)

jp = JSONParser()
jp.parse("data/intents.json")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_random_pattern(jp):
    patterns = []
    for intent in jp.data['intents']:
        if 'subintents' in intent:
            for subintent in intent['subintents']:
                patterns.extend(subintent['patterns'])
    return random.choice(patterns)

def create_inline_keyboard(patterns):
    keyboard = [[InlineKeyboardButton(pattern, callback_data=pattern[:64])] for pattern in patterns]
    return InlineKeyboardMarkup(keyboard)

def create_inline_keyboard_with_tanya(pattern):
    keyboard = [
        [InlineKeyboardButton("Tanya", callback_data=pattern[:64]), InlineKeyboardButton("Pertanyaan Lainnya", callback_data="minta_pertanyaan_lain")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: CallbackContext) -> None:
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await asyncio.sleep(TYPING_DELAY)
    await update.message.reply_text('*Halo!* Anda sedang terhubung dengan chatbot kami yang masih dalam tahap pengembangan. 😊\n\nKami tengah bekerja keras untuk meningkatkan kemampuan chatbot ini agar bisa memberikan informasi yang lebih lengkap dan akurat. Saat ini, chatbot ini dapat memberikan jawaban terbatas, namun tim kami selalu siap membantu jika Anda memerlukan informasi lebih lanjut. 💪\n\nAnda dapat langsung bertanya kepada kami kapan saja, atau gunakan beberapa perintah berikut untuk memulai percakapan:\n\n*Perintah yang tersedia:*\n/start - *Mulai percakapan* dan jelajahi berbagai fitur chatbot kami.\n/tanya - *Ajukan pertanyaan* dan dapatkan rekomendasi terbaik dari chatbot.\n/help - *Panduan lengkap* tentang cara menggunakan chatbot dan fitur-fitur yang ada.\n/bantu - *Dapatkan rekomendasi* pertanyaan yang mungkin menarik untuk ditanyakan.\n\n*Semoga hari Anda menyenangkan!* 😊', parse_mode='Markdown')

async def help_command(update: Update, context: CallbackContext) -> None:
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await asyncio.sleep(TYPING_DELAY)
    await update.message.reply_text("*Untuk memulai percakapan, ketik /start.*\n\nSetelah Anda siap, ketik perintah tersebut untuk mengakses layanan kami.\n\n*Untuk rekomendasi pertanyaan, ketik /tanya.* Gunakan perintah ini untuk mendapatkan rekomendasi pertanyaan dari chatbot kami.\n\n*Untuk mengakhiri chat, ketik 'bye'.* Jika Anda sudah selesai atau ingin berhenti, cukup ketik 'bye' dan percakapan akan berakhir. Kami siap membantu kapan saja!\n\n*Untuk rekomendasi pertanyaan yang menarik, ketik /bantu.* Gunakan perintah ini untuk mendapatkan ide pertanyaan yang bisa Anda tanyakan kepada chatbot kami.\n\n*Semoga informasi ini membantu!* 😊", parse_mode='Markdown')

async def handle_message(update: Update, context: CallbackContext) -> None:
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await asyncio.sleep(TYPING_DELAY)
    user_message = update.message.text
    response, keyboard, tag = bot_response(user_message, pipeline, jp)
    await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)
    if tag == 'bye' or tag == 'bye_umum':
        await update.message.reply_text('*Sampai jumpa!* 👋\n\nTerima kasih banyak telah menjadi bagian dari pengujian chatbot kami. 🙏 Kami sangat menghargai waktu dan masukan Anda yang sangat berharga.', parse_mode='Markdown')

async def random_pattern_command(update: Update, context: CallbackContext) -> None:
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await asyncio.sleep(TYPING_UPDATE_DELAY)
    pattern = get_random_pattern(jp)
    keyboard = create_inline_keyboard_with_tanya(pattern)
    await update.message.reply_text(f"✨ *Rekomendasi Pertanyaan* ✨\nBerikut adalah pertanyaan yang mungkin membantu Anda:\n\n**{pattern}**", reply_markup=keyboard, parse_mode='Markdown')

async def bantu_command(update: Update, context: CallbackContext) -> None:
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await asyncio.sleep(TYPING_DELAY)
    patterns = []
    for intent in jp.data['intents']:
        if 'subintents' in intent:
            for subintent in intent['subintents']:
                patterns.extend(subintent['patterns'])
    random_patterns = random.sample(patterns, 3)
    keyboard = create_inline_keyboard(random_patterns)
    await update.message.reply_text("✨ *Daftar Pertanyaan* ✨\nBerikut adalah beberapa pertanyaan yang mungkin membantu Anda:", reply_markup=keyboard, parse_mode='Markdown')

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_message = query.data

    if user_message == "minta_pertanyaan_lain":
        pattern = get_random_pattern(jp)
        keyboard = create_inline_keyboard_with_tanya(pattern)
        await query.edit_message_text(f"✨ *Rekomendasi Pertanyaan* ✨\nBerikut adalah pertanyaan yang mungkin membantu Anda:\n\n**{pattern}**", reply_markup=keyboard, parse_mode='Markdown')
    else:
        full_message = f"*👤 Anda:* {user_message}"
        await query.edit_message_text(full_message, parse_mode='Markdown')
        await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
        await asyncio.sleep(TYPING_UPDATE_DELAY)
        response, _, tag = bot_response(user_message, pipeline, jp)
        await query.message.reply_text(response, parse_mode='Markdown')

def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("Tidak ada token yang ditemukan di environment variable TELEGRAM_BOT_TOKEN")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("tanya", random_pattern_command))
    application.add_handler(CommandHandler("bantu", bantu_command))
    application.add_handler(CallbackQueryHandler(button))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()