#This script is independet of lib or python version (tested on python 2.7 and 3.5)

import os
import dotenv
import telegram

dotenv.load_dotenv(os.path.join(os.getcwd(), "component\.env"))
my_token = os.getenv("TELEGRAM_BOT_TOKEN")
my_chat = os.getenv("TELEGRAM_CHAT_ID")
bot = telegram.Bot(token=my_token)
print(bot.get_me())

msg_text="Hi," \
         +chr(10)+"Bye"

key1=telegram.InlineKeyboardButton(text="Hi",callback_data="hi")
key2=telegram.InlineKeyboardButton(text="Bye",callback_data="bye")
keyboardBttns = [[key1],[key2]]
keyboardMrkp = telegram.InlineKeyboardMarkup(keyboardBttns)
bot.sendMessage(chat_id=my_chat, text=msg_text, reply_markup=keyboardMrkp) #prod:-1001376715730

