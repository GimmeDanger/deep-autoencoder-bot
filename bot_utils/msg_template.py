class MsgTemplate():
    @staticmethod
    def start_respond():
        return 'start msg respond'

    @staticmethod
    def help_respond():
        return 'help msg respond'
      
    @staticmethod
    def captured_usr_img(sucess=True):
        if sucess:
            return ""
        else:
            return "Oooops! Try again"

    @staticmethod
    def random_img_respond(sucess=True):
        if sucess:
            return ""
        else:
            return "Oooops! Try again"

    @staticmethod
    def get_photo_respond(sucess=True):
        if sucess:
            return "Thanks! \nYour photo is /captured_usr_img"
        else:
            return "Oooops! Try another image"

    @staticmethod
    def default_respond():
        return 'Нажми /help для подробного описания функций бота'
