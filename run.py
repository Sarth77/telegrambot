from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, CallbackContext
from telethon.sync import TelegramClient, events
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
import os

# Get environment variables or use default values
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
PHONE_NUMBER = os.environ.get('PHONE_NUMBER')
APP_URL = os.environ.get("APP_URL")
PORT = int(os.environ.get('PORT'))

# Initialize Telethon client
telethon_client = TelegramClient('session', API_ID, API_HASH)

def start_telethon_handler(event):
    sender = event.sender_id
    chat_id = event.message.peer_id
    if isinstance(chat_id, (PeerUser, PeerChat, PeerChannel)):
        telethon_client.send_message(chat_id, 'Welcome to the bot! How can I assist you?')

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    # Send authentication code
    client = telethon_client.start()

    # Use Telethon to perform advanced actions based on user_id
    update.message.reply_text(f"Welcome! You are now logged in. Your channels: ...")

    # Get all the channels that the user can access
    channels = {d.entity.username: d.entity
                for d in client.get_dialogs()
                if d.is_channel}

    # Prompt the user to select a channel
    print("Available Channels:")
    for username, entity in channels.items():
        print(f"{username} - {entity.title}")

    selected_channel_username = input("Enter the username of the channel you want to view: ")

    # Check if the selected channel username is valid
    if selected_channel_username in channels:
        selected_channel = channels[selected_channel_username]

        # Get the latest chat from the selected channel
        latest_message = client.get_messages(selected_channel, limit=1)[0]

        print(f"\nLatest Chat from {selected_channel_username} - {selected_channel.title}:")
        print(f"{latest_message.sender_id}: {latest_message.text}")

    else:
        print(f"Invalid channel username: {selected_channel_username}")

def login_telethon(phone_number, code):
    # Use Telethon to perform user authentication
    with telethon_client as client:
        client.start()

def main() -> None:
    # Start the Telegram bot
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    
    # Add a MessageHandler to handle /start command from users
    dp.add_handler(MessageHandler(Filters.command & Filters.regex("^/start$"), start_telethon_handler))

    # Start the webhook
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TELEGRAM_BOT_TOKEN, webhook_url=APP_URL + TELEGRAM_BOT_TOKEN)
    updater.idle()

if __name__ == '__main__':
    main()
