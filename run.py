from telegram import Update
from telethon.sync import TelegramClient
from telethon import functions, types
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import threading
import logging
import asyncio
import os

# Define states for the conversation
PHONE, OTP, END = range(3)

# Telethon client setup
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
PHONE_NUMBER = os.environ.get('PHONE_NUMBER')
APP_URL = os.environ.get("APP_URL")
PORT = int(os.environ.get('PORT'))

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

telethon_client = TelegramClient('session', API_ID, API_HASH)

async def send_otp(phone_number):
    await telethon_client.start(phone=phone_number)

async def verify_otp(otp_code):
    try:
        await telethon_client.sign_in(code=otp_code)
        return True
    except Exception as e:
        print(e)
        return False

def start(update, context):
    update.message.reply_text("Please send your phone number in international format (e.g., +1234567890)")
    return PHONE

def phone(update, context):
    phone_number = update.message.text
    asyncio.run(send_otp(phone_number))
    update.message.reply_text("An OTP has been sent to your phone. Please enter the OTP.")
    return OTP

def otp(update, context):
    otp_code = update.message.text
    if asyncio.run(verify_otp(otp_code)):
        update.message.reply_text("You have been successfully connected!")
        return END
    else:
        update.message.reply_text("Invalid OTP. Please try again.")
        return PHONE

def cancel(update, context):
    update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)  # Replace with your bot token
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PHONE: [MessageHandler(Filters.text & ~Filters.command, phone)],
            OTP: [MessageHandler(Filters.text & ~Filters.command, otp)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TELEGRAM_BOT_TOKEN, webhook_url=APP_URL + TELEGRAM_BOT_TOKEN)
    updater.idle()

if __name__ == '__main__':
    main()
