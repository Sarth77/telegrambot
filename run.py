from telegram import Update
from telethon.sync import TelegramClient
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater, ConversationHandler, CallbackContext
import logging
import asyncio
import os

# Define states for the conversation
PHONE, OTP, END = range(3)

# Telethon client setup
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
APP_URL = os.environ.get("APP_URL")
PORT = int(os.environ.get('PORT'))

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

telethon_client = TelegramClient('session', API_ID, API_HASH)

authenticated_users = set()

def help(update: Update, context: CallbackContext) -> None:
    """Sends a help message when the command /help is issued

    Arguments:
        update: update from Telegram
        context: CallbackContext object that stores commonly used objects in handler callbacks
    """

    help_message = "This bot is used to automatically enter trades onto your MetaTrader account directly from Telegram. To begin, ensure that you are selected the correct channel or group from your account to use for copying trading.\n\nThis bot supports all trade order types (Market Execution, Limit, and Stop)\n\nAfter an extended period away from the bot, please be sure to re-enter the start command to restart the connection to your MetaTrader account."
    commands = "List of commands:\n/start : to login in your account\n/help : displays list of commands and example trades\n/trade : takes in user inputted trade for parsing and placement\n/calculate : calculates trade information for a user inputted trade"
    trade_example = "Example Trades 💴:\n\n"
    market_execution_example = "Market Execution:\nBUY GBPUSD\nEntry NOW\nSL 1.14336\nTP 1.28930\nTP 1.29845\n\n"
    limit_example = "Limit Execution:\nBUY LIMIT GBPUSD\nEntry 1.14480\nSL 1.14336\nTP 1.28930\n\n"
    note = "You are able to enter up to two take profits. If two are entered, both trades will use half of the position size, and one will use TP1 while the other uses TP2.\n\nNote: Use 'NOW' as the entry to enter a market execution trade."

    # sends messages to user
    update.effective_message.reply_text(help_message)
    update.effective_message.reply_text(commands)
    update.effective_message.reply_text(trade_example + market_execution_example + limit_example + note)

    return
def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation.   
    
    Arguments:
        update: update from Telegram
        context: CallbackContext object that stores commonly used objects in handler callbacks
    """

    update.effective_message.reply_text("Command has been canceled.")

    # removes trade from user context data
    context.user_data['trade'] = None

    return ConversationHandler.END

def error(update: Update, context: CallbackContext) -> None:
    """Logs Errors caused by updates.

    Arguments:
        update: update from Telegram
        context: CallbackContext object that stores commonly used objects in handler callbacks
    """

    logger.warning('Update "%s" caused error "%s"', update, context.error)

    return

def unknown_command(update: Update, context: CallbackContext) -> None:
    """Checks if the user is authorized to use this bot or shares to use /help command for instructions.

    Arguments:
        update: update from Telegram
        context: CallbackContext object that stores commonly used objects in handler callbacks
    """
    if update.effective_message.chat.username not in authenticated_users:
        update.effective_message.reply_text("You are not authorized to use this bot! 🙅🏽‍♂️")
        return PHONE

    update.effective_message.reply_text("Unknown command. Use /trade to place a trade or /calculate to find information for a trade. You can also use the /help command to view instructions for this bot.")

    return

async def send_otp(update, context):
    phone_number = context.user_data.get('phone_number')
    
    # Connect the client if not already connected
    if not telethon_client.is_connected():
        await telethon_client.connect()
        
    # Check if the user is already authorized
    if await telethon_client.is_user_authorized():
        update.effective_message.reply_text("You are already logged in.")
        return ConversationHandler.END      
    else:
        login_token = await telethon_client.sign_in(phone_number)
        context.user_data['login_token'] = login_token
        update.effective_message.reply_text("Please enter the OTP.")
        return OTP  # Indicates that OTP was sent
        
async def otp(update, context):
    otp_code = update.effective_message.text
    phone_number = context.user_data.get('phone_number')
    login_token = context.user_data.get('login_token')
    try:
        user_or_token = await telethon_client.sign_in(login_token, code=otp_code)
        update.effective_message.reply_text("You have been successfully connected!",user_or_token)
        return ConversationHandler.END
    except Exception as e:
        print(e)
        update.effective_message.reply_text("Invalid OTP. Please try again.")
        return OTP
    
def phone(update, context):
    phone_number = update.effective_message.text
    context.user_data['phone_number'] = phone_number
    asyncio.run(send_otp(update, context))

def welcome(update: Update, context: CallbackContext) -> str:
    """Sends welcome message to user.

    Arguments:
        update: update from Telegram
        context: CallbackContext object that stores commonly used objects in handler callbacks
    """

    welcome_message = "Welcome to the FX Signal Copier Telegram Bot! 💻💸\n\nYou can use this bot to enter trades directly from Telegram and get a detailed look at your risk to reward ratio with profit, loss, and calculated lot size.\n\nIn order to get started please send your phone number in international format (e.g., +1234567890)\n\nUse the /help command to view instructions and example trades."
    
    # sends messages to user
    update.effective_message.reply_text(welcome_message)
    
    return PHONE



def main() -> None:
    """Runs the Telegram bot."""

    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)

    # get the dispatcher to register handlers
    dp = updater.dispatcher

    # help command handler
    dp.add_handler(CommandHandler("help", help))
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', welcome)],
        states={
            PHONE: [MessageHandler(Filters.text & ~Filters.command, phone)],
            # OTP: [MessageHandler(Filters.text & ~Filters.command, otp)],
            # TRADE: [MessageHandler(Filters.text & ~Filters.command, PlaceTrade)],
            # CALCULATE: [MessageHandler(Filters.text & ~Filters.command, CalculateTrade)],
            # DECISION: [CommandHandler("yes", PlaceTrade), CommandHandler("no", cancel)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # conversation handler for entering trade or calculating trade information
    dp.add_handler(conv_handler)

    # message handler for all messages that are not included in conversation handler
    dp.add_handler(MessageHandler(Filters.text, unknown_command))

    # log all errors
    dp.add_error_handler(error)
    
    # listens for incoming updates from Telegram
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TELEGRAM_BOT_TOKEN, webhook_url=APP_URL + TELEGRAM_BOT_TOKEN)
    updater.idle()

    return

if __name__ == '__main__':
    main()
