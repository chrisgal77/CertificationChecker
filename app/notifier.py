from notifypy import Notify


class Notifier:
    def __init__(self):
        self.notification = Notify()

    def send_message(self, title, message):
        self.notification.title = title
        self.notification.message = message
        self.notification.send()
