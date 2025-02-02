import telebot
from telebot import apihelper
from itertools import cycle

import numpy as np
from random import randint
from skimage.io import imread, imsave

class TelebotWrapper(telebot.TeleBot):

    # tracking user data
    # (user id : {random_img, normal_code, user_img}
    captured_data_dict = dict()
    # (user id : {emotional_img}
    emotional_data_dict = dict()
    
    # preloaded resized dataset for examples
    dataset = np.load("autoencoder/lfw_dataset/data_90.npy").astype('float32') / 255.

    # proxy switching list,
    # thanks to https://github.com/uburuntu
    # for this idea and his ispiring bots
    curr_proxy = cycle([
        '',
        'socks5://telegram:telegram@sr123.spry.fail:1080',
        'socks5://telegram:telegram@sreju5h4.spry.fail:1080',
        'socks5://28006241:F1zcUqql@deimos.public.opennetwork.cc:1090',
        'socks5://telegram:telegram@rmpufgh1.teletype.live:1080',
        'socks5://28006241:F1zcUqql@phobos.public.opennetwork.cc:1090',
    ])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apihelper.CONNECT_TIMEOUT = 2.5

    def set_proxy(self):
        apihelper.proxy = {'https': next(self.curr_proxy)}
        apihelper._get_req_session(reset=True)      
        
        
    ######################################################    
    
    # TODO: convert without dumping
    # this function is very disgusting
    @staticmethod
    def to_photo(np_img):
      np_img = (np_img - np.min(np_img)) / (np.max(np_img) - np.min(np_img))
      imsave('tmp.jpg', np_img)
      photo = open('tmp.jpg', 'rb')
      return photo
        
    def capture_data_random_img(self, user_id):
      rand_i = randint(0, len(self.dataset)-1)
      self.captured_data_dict[user_id] = (self.dataset[rand_i], None, None)
      self.emotional_data_dict[user_id] = None
      
    def capture_data_normal_code(self, user_id, normal_code):
      self.captured_data_dict[user_id] = (None, normal_code, None)
      self.emotional_data_dict[user_id] = None
      
    def capture_data_user_img(self, user_id, img):
      self.captured_data_dict[user_id] = (None, None, img)
      self.emotional_data_dict[user_id] = None
      
    def capture_data_emotional_img(self, user_id, img):
      self.emotional_data_dict[user_id] = img

    def get_captured_data_normal_code(self, user_id):
      if (user_id not in self.captured_data_dict) or (user_id not in self.emotional_data_dict):
        return None, None
      val, emotional_val = self.captured_data_dict[user_id], self.emotional_data_dict[user_id] 
      return 
      
    def get_captured_data_random_img(self, user_id):
      if (user_id not in self.captured_data_dict) or (user_id not in self.emotional_data_dict):
        return None, None
      return self.captured_data_dict[user_id][0], self.emotional_data_dict[user_id]

    def get_captured_data_normal_code(self, user_id):
      if (user_id not in self.captured_data_dict) or (user_id not in self.emotional_data_dict):
        return None, None
      return self.captured_data_dict[user_id][1], self.emotional_data_dict[user_id]

    def get_captured_data_user_img(self, user_id):
      if (user_id not in self.captured_data_dict) or (user_id not in self.emotional_data_dict):
        return None, None
      return self.captured_data_dict[user_id][2], self.emotional_data_dict[user_id]        
