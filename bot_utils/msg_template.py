class MsgTemplate():
    @staticmethod
    def start_respond():
        return 'start msg respond'

    @staticmethod
    def help_respond():
        return 'help msg respond'

    @staticmethod
    def get_photo_respond(sucess=True):
        if sucess:
            return "thanks! now your photo is captured"
        else:
            return "ooops! try another image"

    @staticmethod
    def default_respond():
        return 'Send a photo or press /help'