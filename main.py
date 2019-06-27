import time
import os
import sys
import requests
import random
import re

import tokens
import telebot
from bot_utils import TelebotWrapper
from telebot.types import InlineKeyboardButton as Button, InlineKeyboardMarkup

bot = TelebotWrapper(tokens.bot, threaded=False)

def commands_handler(cmnds):
    def wrapped(message):
        if not message.text:
            return False
        split_message = re.split(r'[^\w@/]', message.text.lower())
        s = split_message[0]
        return (s in cmnds) or (s.split('@')[0] in cmnds)
    return wrapped

@bot.message_handler(func=commands_handler(['/start']))
def command_start(message):
    msg = "Привет! Перед вами бот"
    bot.send_message(message.chat.id, msg)
    
@bot.message_handler(func=commands_handler(['/help']))
def command_help(message):
    msg = "help text"
    bot.send_message(message.chat.id, msg)  
    
def heheh(call):
  print(12312312)
  message = call.message
  text = '12312'
  bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=text, parse_mode='HTML')
  #bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id, reply_markup=keyboard)
  bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=text)    
    
@bot.callback_query_handler(func=lambda call: call.data.startswith('heheh'))
def callback_in_office(call):
    heheh(call)
    
@bot.message_handler(func=commands_handler(['/captured_img']))
def command_start(message):
    text = 'you are my best friend'
    keyboard = InlineKeyboardMarkup()
    keyboard.add(Button(text='⬅️', callback_data='heheh'),
                 Button(text='➡️➡️➡️', callback_data='ahaha'),)
    bot.reply_to(message, text, reply_markup=keyboard, parse_mode='HTML')

# add capture image command
    
#@bot.message_handler(commands=['randompepe'])    
@bot.message_handler(content_types=['photo'])
def photo(message):
    print('message.photo =', message.photo)
    fileID = message.photo[-1].file_id
    print('fileID =', fileID)
    file_info = bot.get_file(fileID)
    print('file.file_path =', file_info.file_path)
    try:
      downloaded_file = bot.download_file(file_info.file_path)
      with open("image.jpg", 'wb') as new_file:
          new_file.write(downloaded_file)    
      
      msg = "thanks!"
      bot.send_message(message.chat.id, msg)
      
      file= open('uvojenie.png','rb')
      bot.send_photo(message.chat.id, file);
      
    except:
      msg = "ooops! try another image"    
      bot.send_message(message.chat.id, msg)

    
@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    msg = "Send a photo or press /help"
    bot.send_message(message.chat.id, msg)

if __name__ == '__main__':
    while True:
        try:
            bot.set_proxy()
            bot.polling(none_stop=True)

        except requests.exceptions.ReadTimeout as e:
            print('Read Timeout. Reconnecting in 5 seconds.')
            time.sleep(5)

        except requests.exceptions.ConnectionError as e:
            print('Connection Error. Reconnecting...')
            time.sleep(1)

        except KeyboardInterrupt as e:
            print('Keyboard Interrupt. Good bye.')
            sys.exit(0)