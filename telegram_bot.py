import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
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
    if max_prob < 0.05:
        return "Maaf, saya tidak mengerti, jika anda butuh bantuan harap menghubungi humas kami.", None
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

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hi! Anda terhubung dengan chatbot kami.')

async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Untuk memulai chat, ketik /start. Untuk mengakhiri chat, ketik 'bye'")

async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    response, tag = bot_response(user_message, pipeline, jp)
    await update.message.reply_text(response)
    if tag == 'bye' or tag == 'bye_umum':
        await update.message.reply_text('Sampai jumpa!')

def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("Tidak ada token yang ditemukan di environment variable TELEGRAM_BOT_TOKEN")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()