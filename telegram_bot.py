import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import pickle
import numpy as np
import string
from util.parser import JSONParser
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fungsi preprocess
def preprocess(chat):
    # konversi ke non kapital
    chat = chat.lower()
    # hilangkan tanda baca
    tandabaca = tuple(string.punctuation)
    chat = ''.join(ch for ch in chat if ch not in tandabaca)
    return chat

# Fungsi bot_response
def bot_response(chat, pipeline, jp):
    chat = preprocess(chat)
    res = pipeline.predict_proba([chat])
    max_prob = max(res[0])
    if max_prob < 0.2:
        return "Maaf, saya tidak mengerti, jika anda butuh bantuan harap menghubungi humas kami.", None
    else:
        max_id = np.argmax(res[0])
        pred_tag = pipeline.classes_[max_id]
        return jp.get_response(pred_tag), pred_tag

# Load model
with open("model_chatbot.pkl", "rb") as model_file:
    pipeline = pickle.load(model_file)

# Load JSONParser and other necessary components
jp = JSONParser()
jp.parse("data/intents.json")

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi! Anda terhubung dengan chatbot kami.')

async def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Untuk memulai chat, ketik /start. Untuk mengakhiri chat, ketik 'bye'")

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle the user message."""
    user_message = update.message.text
    response, tag = bot_response(user_message, pipeline, jp)
    await update.message.reply_text(response)
    if tag == 'bye':
        await update.message.reply_text('Sampai jumpa!')

def main() -> None:
    """Start the bot."""
    # Get the bot token from environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("Tidak ada token yang ditemukan di environment variable TELEGRAM_BOT_TOKEN")

    # Create the Application and pass it your bot token.
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()