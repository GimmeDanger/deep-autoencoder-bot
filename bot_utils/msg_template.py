class MsgTemplate():
    @staticmethod
    def start_respond():
        ret = None
        with open('data/cmd_start.html', 'r', encoding='utf-8') as file:
            ret = file.read()
        return ret

    @staticmethod
    def help_respond():
        ret = None
        with open('data/cmd_help.html', 'r', encoding='utf-8') as file:
            ret = file.read()
        return ret
      
    @staticmethod
    def captured_usr_img(sucess=True):
        if sucess:
            return ""
        else:
            return "Oooops! Попробуй сначала прислать мне фото"

    @staticmethod
    def random_img_respond(sucess=True):
        if sucess:
            return ""
        else:
            return "Oooops! Попробуй ещё раз"

    @staticmethod
    def get_photo_respond(sucess=True):
        if sucess:
            return "Отличино! \nВаше фото теперь в \n/captured_usr_img"
        else:
            return "Oooops! Попробуй другое фото"

    @staticmethod
    def default_respond():
        return 'Нажми /help для подробного описания функций бота'
