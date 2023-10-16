class Messages:
    def __init__(self, date, text, users, hastags):
        self.date = date
        self.text = text
        self.users = users
        self.hashtags = hastags

    def get_date(self):
        return self.date

    def get_text(self):
        return self.text

    def get_users(self):
        return self.users

    def get_hashtags(self):
        return self.hashtags

    def set_users(self, users):
        self.users = users

    def set_hashtags(self, hashtags):
        self.hashtags = hashtags

    def __str__(self):
        text = f"Fecha: {self.date}:\nTexto: {self.text}\nUsuarios: {self.users}\nhashtags: {self.hashtags}"
        return text