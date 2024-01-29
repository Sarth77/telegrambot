from telegram import ParseMode, Update
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater, ConversationHandler, CallbackContext
from telethon import TelegramClient, events


# Get environment variables or use default values
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
PHONE_NUMBER = os.environ.get('PHONE_NUMBER')
APP_URL = os.environ.get("APP_URL")
PORT = int(os.environ.get('PORT'))

# Initialize Telethon client
client = TelegramClient('session', API_ID, API_HASH).start(bot_token=TELEGRAM_BOT_TOKEN)

def start(update: Update, context: CallbackContext) -> None:

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


def main() -> None:
    # Start the Telegram bot
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    # Start the webhook
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TELEGRAM_BOT_TOKEN, webhook_url=APP_URL + TELEGRAM_BOT_TOKEN)
    updater.idle()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
