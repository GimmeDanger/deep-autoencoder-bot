from telebot import Telebot, apihelper
from itertools import cycle


class TelebotWrapper(telebot.TeleBot):

    # tracking user id
    id_set = set()

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
