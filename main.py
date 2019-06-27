import time
import sys
import requests
import re

import numpy as np

from autoencoder.model import Autoencoder
from skimage.io import imread, imsave

import tokens
import telebot
from bot_utils.telebot_wrapper import TelebotWrapper
from bot_utils.msg_template import MsgTemplate
from telebot.types import InlineKeyboardButton as Button, InlineKeyboardMarkup, InputMediaPhoto


bot = TelebotWrapper(tokens.bot, threaded=False)
ae = Autoencoder(encoder_weights_path='autoencoder/model_weights/encoder_weights.txt',
                 decoder_weights_path='autoencoder/model_weights/decoder_weights.txt',
                 happiness_code_path='autoencoder/model_weights/happiness_code_90.npy')

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
  bot.reply_to(message, MsgTemplate.start_respond(), parse_mode='HTML', disable_web_page_preview=True)
    
@bot.message_handler(func=commands_handler(['/help']))
def command_help(message):
  bot.reply_to(message, MsgTemplate.help_respond(), parse_mode='HTML', disable_web_page_preview=True)
    
    
################ Capturing random image from dataset  ######################  


def random_img_predict_keyboard():
  keyboard = InlineKeyboardMarkup()
  keyboard.add(Button(text='🤖(predict)', callback_data='random_img_predict'),
               Button(text='🎲(dice)', callback_data='random_img_dice'),)
  return keyboard

def random_img_modify_keyboard():
  keyboard = InlineKeyboardMarkup()
  keyboard.add(Button(text='😁', callback_data='random_img_add_happiness'),               
               Button(text='🤦(back)', callback_data='random_img_restore'),
               Button(text='😒', callback_data='random_img_sub_happiness'),)
  return keyboard

@bot.callback_query_handler(func=lambda call: call.data.startswith('random_img_dice'))
def callback_random_img_dice(call):
    bot.capture_data_emotional_img(call.message.chat.id, None)
    bot.capture_data_random_img(call.message.chat.id)
    np_img, _ = bot.get_captured_data_random_img(call.message.chat.id)
    if np_img is not None:
      photo = TelebotWrapper.to_photo(np_img)
      bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                             media=InputMediaPhoto(photo), reply_markup=random_img_predict_keyboard())
      bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
      
@bot.callback_query_handler(func=lambda call: call.data.startswith('random_img_restore'))
def callback_random_img_predict(call):
    bot.capture_data_emotional_img(call.message.chat.id, None)
    np_img, _ = bot.get_captured_data_random_img(call.message.chat.id)
    if np_img is not None:
      photo = TelebotWrapper.to_photo(np_img)
      bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                             media=InputMediaPhoto(photo), reply_markup=random_img_predict_keyboard())
      bot.answer_callback_query(callback_query_id=call.id, show_alert=False)      

@bot.callback_query_handler(func=lambda call: call.data.startswith('random_img_predict'))
def callback_random_img_predict(call):
    np_img, _ = bot.get_captured_data_random_img(call.message.chat.id)
    if np_img is not None:
      ae_res = ae.predict_img(np_img)
      photo = TelebotWrapper.to_photo(ae_res)
      bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                             media=InputMediaPhoto(photo), reply_markup=random_img_modify_keyboard())
      bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
  
# inverse=False for 'add_happiness
# inverse=True for 'sub_happiness
def add_random_img_happiness_wrapper(call, inverse=False):
    np_img, np_emotional_img = bot.get_captured_data_random_img(call.message.chat.id)
    if np_img is not None:
      if np_emotional_img is None:
        np_emotional_img = np_img
      
      # predict and save  
      res = ae._add_happiness(np_emotional_img, inverse)  
      bot.capture_data_emotional_img(call.message.chat.id, res)
      
      emotional_photo = TelebotWrapper.to_photo(res)      
      bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                             media=InputMediaPhoto(emotional_photo), reply_markup=random_img_modify_keyboard())
      bot.answer_callback_query(callback_query_id=call.id, show_alert=False)  
      
@bot.callback_query_handler(func=lambda call: call.data.startswith('random_img_add_happiness'))
def callback_random_img_add_happiness(call):
    add_random_img_happiness_wrapper(call)
      
@bot.callback_query_handler(func=lambda call: call.data.startswith('random_img_sub_happiness'))
def callback_random_img_add_happiness(call):
    add_random_img_happiness_wrapper(call, inverse=True)       
      
    
@bot.message_handler(func=commands_handler(['/random_img']))
def command_random_img(message):
    bot.capture_data_random_img(message.chat.id)
    np_img, _ = bot.get_captured_data_random_img(message.chat.id)
    if np_img is not None:
      photo = TelebotWrapper.to_photo(np_img)
      bot.send_photo(message.chat.id, photo, reply_to_message_id=message.message_id,
                     reply_markup=random_img_predict_keyboard())
    else:
      bot.send_message(message.chat.id, MsgTemplate.random_img_respond(success=False))  
      
      
################ Capturing normal code image  ######################        

def normal_code_modify_keyboard():
  keyboard = InlineKeyboardMarkup()
  keyboard.add(Button(text='😁', callback_data='normal_code_add_happiness'),    
               Button(text='🎃(booo)', callback_data='normal_code_dice'),
               Button(text='😒', callback_data='normal_code_sub_happiness'),)
  return keyboard

@bot.callback_query_handler(func=lambda call: call.data.startswith('normal_code_dice'))
def callback_normal_code_dice(call):
    bot.capture_data_emotional_img(call.message.chat.id, None)
    mu, sigma = np.random.uniform(0., 5., 1), np.random.uniform(0., 16., 1)
    normal_code = np.random.normal(mu, sigma, ae.code_size) 
    bot.capture_data_normal_code(call.message.chat.id, normal_code)    
    np_img, _ = bot.get_captured_data_normal_code(call.message.chat.id)
    if np_img is not None:
      res = ae._predict_code_reconstruction(np_img)      
      photo = TelebotWrapper.to_photo(res)
      bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                             media=InputMediaPhoto(photo, caption=f'(µ, σ) = ({mu:.3f}, {sigma:.3f})'),
                             reply_markup=normal_code_modify_keyboard())
      bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
      
# inverse=False for 'add_happiness
# inverse=True for 'sub_happiness
def add_normal_code_img_happiness_wrapper(call, inverse=False):
    np_code, np_emotional_code = bot.get_captured_data_normal_code(call.message.chat.id)
    if np_code is not None:
      if np_emotional_code is None:
        np_emotional_code = np_code
        
      # make the code happier, save it and reconstruct img
      happy_img_code = ae._get_happy_img_code(np_emotional_code, inverse)      
      bot.capture_data_emotional_img(call.message.chat.id, happy_img_code)
      happy_img = ae.decoder.predict(happy_img_code[None])[0]
      
      emotional_photo = TelebotWrapper.to_photo(happy_img)      
      bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                             media=InputMediaPhoto(emotional_photo), reply_markup=normal_code_modify_keyboard())
      bot.answer_callback_query(callback_query_id=call.id, show_alert=False)  
      
@bot.callback_query_handler(func=lambda call: call.data.startswith('normal_code_add_happiness'))
def callback_normal_code_add_happiness(call):
    add_normal_code_img_happiness_wrapper(call)
      
@bot.callback_query_handler(func=lambda call: call.data.startswith('normal_code_sub_happiness'))
def callback_normal_code_add_happiness(call):
    add_normal_code_img_happiness_wrapper(call, inverse=True)          

@bot.message_handler(func=commands_handler(['/normal_code_img']))
def command_normal_code_img(message):    
    def validate(s):
      try:
          s = float(s)
          if s < 0. or s > 255.:
            return False
          return True
      except ValueError:
        return False
      
    split = message.text.split()
    
    if len(split) == 3 and validate(split[1]) and validate(split[2]):
      mu, sigma = float(split[1]), float(split[2])          
      normal_code = np.random.normal(mu, sigma, ae.code_size) 
      bot.capture_data_normal_code(message.chat.id, normal_code)
      res = ae._predict_code_reconstruction(normal_code)      
      photo = TelebotWrapper.to_photo(res)
      bot.send_photo(message.chat.id, photo, caption=f'(µ, σ) = ({mu:.3f}, {sigma:.3f})',
                     reply_to_message_id=message.message_id, reply_markup=normal_code_modify_keyboard())
    else:
        ans = "Использование: /normal_code_img [µ] [σ], где µ, σ - параметры нормального \
               распределения в диапазоне 0 до 255. Если любите классику, то используйте (µ, σ) = (0, 1)."
        bot.reply_to(message, ans)

@bot.message_handler(func=commands_handler(['/normal_code_img_0_1']))
def command_normal_code_img_0_1(message):    
    mu, sigma = 0, 1      
    normal_code = np.random.normal(mu, sigma, ae.code_size) 
    bot.capture_data_normal_code(message.chat.id, normal_code)
    res = ae._predict_code_reconstruction(normal_code)      
    photo = TelebotWrapper.to_photo(res)
    bot.send_photo(message.chat.id, photo, caption=f'(µ, σ) = ({mu:.3f}, {sigma:.3f})',
                   reply_to_message_id=message.message_id, reply_markup=normal_code_modify_keyboard())

#################### Capturing user image  #########################

@bot.message_handler(content_types=['photo'])
def photo(message):    
    try:
      # Download sended photo
      file_info = bot.get_file(message.photo[-1].file_id)
      downloaded_file = bot.download_file(file_info.file_path)
      with open("image.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)
      user_img = imread("image.jpg")      
            
      # Save photo
      bot.capture_data_user_img(message.chat.id, user_img)
            
      # send some respect      
      bot.send_photo(message.chat.id, open('data/uvojenie.png','rb'))
      bot.send_message(message.chat.id, MsgTemplate.get_photo_respond(sucess=True))      
      
    except:
      bot.send_message(message.chat.id, MsgTemplate.get_photo_respond(sucess=False))


def user_img_predict_keyboard():
  keyboard = InlineKeyboardMarkup()
  keyboard.add(Button(text='🤖(predict)', callback_data='user_img_predict'),)
  return keyboard

def user_img_modify_keyboard():
  keyboard = InlineKeyboardMarkup()
  keyboard.add(Button(text='😁', callback_data='user_img_add_happiness'),    
               Button(text='🤦', callback_data='user_img_restore'),
               Button(text='😒', callback_data='user_img_sub_happiness'),)
  return keyboard  

@bot.callback_query_handler(func=lambda call: call.data.startswith('user_img_restore'))
def callback_user_img_predict(call):
    bot.capture_data_emotional_img(call.message.chat.id, None)    
    usr_img, _ = bot.get_captured_data_user_img(call.message.chat.id)
    if usr_img is not None:
      ae_format, _ = ae.feed_photo(usr_img)
      photo = TelebotWrapper.to_photo(ae_format)
      bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                             media=InputMediaPhoto(photo), reply_markup=user_img_predict_keyboard())
      bot.answer_callback_query(callback_query_id=call.id, show_alert=False)      

@bot.callback_query_handler(func=lambda call: call.data.startswith('user_img_predict'))
def callback_user_img_predict(call):
    user_img, _ = bot.get_captured_data_user_img(call.message.chat.id)
    if user_img is not None:
      _, ae_res = ae.feed_photo(user_img)
      photo = TelebotWrapper.to_photo(ae_res)
      caption_txt = "Сеть немнооого переобучилась... Лучше попробуйте поиграть c /random_img или /normal_code_img. \
                     Либо хорошо обрежьте изображение, чтобы больше напоминало примеры и /random_img."
      bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                             media=InputMediaPhoto(photo, caption=caption_txt),
                             reply_markup=user_img_modify_keyboard())
      bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
  
# inverse=False for 'add_happiness
# inverse=True for 'sub_happiness
def add_user_img_happiness_wrapper(call, inverse=False):
    user_img, user_emotional_img = bot.get_captured_data_user_img(call.message.chat.id)
    if user_img is not None:
      user_emotional_img = user_img
      happy_img = ae.add_happiness(user_emotional_img, inverse)
      emotional_img = TelebotWrapper.to_photo(happy_img)
      bot.capture_data_emotional_img(call.message.chat.id, emotional_img)
      
      bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                             media=InputMediaPhoto(emotional_img), reply_markup=user_img_modify_keyboard())
      bot.answer_callback_query(callback_query_id=call.id, show_alert=False)  
      
@bot.callback_query_handler(func=lambda call: call.data.startswith('user_img_add_happiness'))
def callback_user_img_add_happiness(call):
    add_user_img_happiness_wrapper(call)
      
@bot.callback_query_handler(func=lambda call: call.data.startswith('user_img_sub_happiness'))
def callback_user_img_sub_happiness(call):
    add_user_img_happiness_wrapper(call, inverse=True)  
    
@bot.message_handler(func=commands_handler(['/captured_usr_img']))
def command_captured_usr_img(message):
    user_img, _ = bot.get_captured_data_user_img(message.chat.id)    
    if user_img is not None:
      ae_format, _ = ae.feed_photo(user_img)
      photo = TelebotWrapper.to_photo(ae_format)
      bot.send_photo(message.chat.id, photo, reply_to_message_id=message.message_id,
                     reply_markup=user_img_predict_keyboard())
    else:
      bot.send_message(message.chat.id, MsgTemplate.captured_usr_img(sucess=False))

############# Other messages if no handler has been triggered  ##############

@bot.message_handler(content_types=["text"])
def other_messages(message):
    bot.send_message(message.chat.id, MsgTemplate.default_respond())


######################### Main loop  ########################################


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
