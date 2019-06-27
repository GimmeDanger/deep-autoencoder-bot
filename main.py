import time
import sys
import requests
import re

from autoencoder.model import Autoencoder
from skimage.io import imread, imsave

import tokens
import telebot
from bot_utils.telebot_wrapper import TelebotWrapper
from bot_utils.msg_template import MsgTemplate
from telebot.types import InlineKeyboardButton as Button, InlineKeyboardMarkup, InputMediaPhoto


bot = TelebotWrapper(tokens.bot, threaded=False)
ae = Autoencoder(load_pretrained_weights=True,
                 encoder_weights_path='autoencoder/model_weights/encoder_weights.txt',
                 decoder_weights_path='autoencoder/model_weights/decoder_weights.txt')

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
    bot.send_message(message.chat.id, MsgTemplate.start_respond())
    
@bot.message_handler(func=commands_handler(['/help']))
def command_help(message):
    bot.send_message(message.chat.id, MsgTemplate.help_respond())
    
    
################ Capturing random image from dataset  ######################  


def random_img_predict_keybord():
  keyboard = InlineKeyboardMarkup()
  keyboard.add(Button(text='🤖', callback_data='random_img_predict'),
               Button(text='🎲', callback_data='random_img_dice'),)
  return keyboard

def random_img_restore_keybord():
  keyboard = InlineKeyboardMarkup()
  keyboard.add(Button(text='🤦', callback_data='random_img_restore'),
               Button(text='🎲', callback_data='random_img_dice'),)
  return keyboard

@bot.callback_query_handler(func=lambda call: call.data.startswith('random_img_dice'))
def callback_random_img_dice(call):
    bot.capture_data_random_img(call.message.chat.id)
    np_img = bot.get_captured_data(call.message.chat.id)
    if np_img is not None:
      photo = TelebotWrapper.to_photo(np_img)
      bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                             media=InputMediaPhoto(photo), reply_markup=random_img_predict_keybord())
      bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
      
@bot.callback_query_handler(func=lambda call: call.data.startswith('random_img_restore'))
def callback_random_img_predict(call):
    np_img = bot.get_captured_data(call.message.chat.id)
    if np_img is not None:
      photo = TelebotWrapper.to_photo(np_img)
      bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                             media=InputMediaPhoto(photo), reply_markup=random_img_predict_keybord())
      bot.answer_callback_query(callback_query_id=call.id, show_alert=False)      

@bot.callback_query_handler(func=lambda call: call.data.startswith('random_img_predict'))
def callback_random_img_predict(call):
    np_img = bot.get_captured_data(call.message.chat.id)
    if np_img is not None:
      ae_res = ae.predict_img(np_img/255.)
      photo = TelebotWrapper.to_photo(ae_res)
      bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                             media=InputMediaPhoto(photo), reply_markup=random_img_restore_keybord())
      bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
      
    
@bot.message_handler(func=commands_handler(['/random_img']))
def command_random_img(message):
    bot.capture_data_random_img(message.chat.id)
    np_img = bot.get_captured_data(message.chat.id)
    if np_img is not None:
      photo = TelebotWrapper.to_photo(np_img)
      bot.send_photo(message.chat.id, photo, reply_to_message_id=message.message_id,
                     reply_markup=random_img_predict_keybord())
    else:
      bot.send_message(message.chat.id, MsgTemplate.random_img_respond(success=False))  
      
      
################ Capturing random image from dataset  ######################        
    
def add_happiness(call):
  message = call.message  
  file_id = call.message.photo[-1].file_id
  file_info = bot.get_file(file_id)
  #img = bot.download_file(file_info.file_path)  
  with open('image.jpg', 'rb') as img:
    bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                           media=InputMediaPhoto(img), reply_markup=captured_img_keybord())
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
  
    
@bot.callback_query_handler(func=lambda call: call.data.startswith('add_happiness'))
def callback_in_office(call):
    add_happiness(call)
    
@bot.message_handler(func=commands_handler(['/captured_img']))
def command_start(message):
    np_img = bot.get_captured_data(message.chat.id)    
    if np_img is not None:
      img = TelebotWrapper.to_photo(np_img)
      bot.send_photo(message.chat.id, img, reply_to_message_id=message.message_id, reply_markup=captured_img_keybord())

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
      
      file= open('uvojenie.png','rb')
      bot.send_photo(message.chat.id, file)
      bot.send_message(message.chat.id, MsgTemplate.get_photo_respond(sucess=True))

      #test
      user_img = imread("image.jpg")  
      ae_format, ae_res = ae.feed_photo(user_img)
      imsave('formatted_image.jpg', ae_format)
      imsave('reconstr_image.jpg', ae_res)
      send_formated_img = open('formatted_image.jpg', 'rb')
      send_res_img = open('reconstr_image.jpg', 'rb')
      bot.send_photo(message.chat.id, send_formated_img)
      bot.send_photo(message.chat.id, send_res_img)
      
    except:
      bot.send_message(message.chat.id, MsgTemplate.get_photo_respond(sucess=False))        


@bot.message_handler(content_types=["text"])
def other_messages(message):
    bot.send_message(message.chat.id, MsgTemplate.default_respond())


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
