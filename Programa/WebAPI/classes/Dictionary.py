class Dictionary:
    def __init__(self):
        self.positive_feelings = []
        self.negative_feelings = []
        self.positive_rejected = []
        self.negative_rejected = []

    def get_positive_feelings(self):
        return self.positive_feelings

    def get_negative_feelings(self):
        return self.negative_feelings

    def get_positive_rejected(self):
        return self.positive_rejected

    def get_negative_rejected(self):
        return self.negative_rejected

    def add_feeling(self, feeling, type_feeling):
        list_feeling = None
        list_rejected = None
        if type_feeling == "Negative":
            list_feeling = self.negative_feelings
            list_rejected = self.positive_rejected
        elif type_feeling == "Positive":
            list_feeling = self.positive_feelings
            list_rejected = self.negative_rejected

        if feeling not in self.get_negative_feelings() or feeling not in self.get_positive_feelings():
            list_feeling.append(feeling)
        elif feeling not in list_rejected:
            list_rejected.append(feeling)

    def __str__(self):
        text = f"Sentimientos Positivos:\n\t{self.positive_feelings}\n"
        text += f"Sentimientos Negativos:\n\t{self.negative_feelings}\n"
        text += f"Sentimientos Positivos Rechazados:\n\t{self.positive_rejected}\n"
        text += f"Sentimientos Negativos Rechazados:\n\t{self.negative_rejected}\n"
        return text