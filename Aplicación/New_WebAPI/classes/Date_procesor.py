from classes.Data_base import *


class Data_procesor:
    def __init__(self):
        self.date_one = None
        self.date_two = None
        self.Data_base = Data_base()

    def format_dates(self, request):
        self.date_one = request.args.get('date_1')
        self.date_two = request.args.get('date_2')
        if self.date_one is None or self.date_two is None:
            return {'error': 'Las fechas no se proporcionaron correctamente'}

        try:
            date_one = datetime.strptime(self.date_one, "%d/%m/%Y")
            date_two = datetime.strptime(self.date_two, "%d/%m/%Y")
            self.Data_base.set_dates(date_one, date_two)
        except ValueError:
            return {'error': 'El formato de fecha no es válido'}

        if date_one > date_two:
            return {'error': f"{date_one} es posterior a {date_two}"}
        elif date_one < date_two:
            return {'dates': [date_one, date_two]}
        else:
            return {'dates': [date_one, date_two]}

    def get_hashtags(self, request):
        data = self.format_dates(request)
        if 'error' in data:
            error_message = data['error']
            return {'error': error_message}
        else:
            response = self.Data_base.process_data('HASHTAGS')

            # Procesar los resultados de hashtags para obtener la cantidad total
            total_hashtags = {}
            for date_data in response.values():
                for hashtag, count in date_data.items():
                    if hashtag in total_hashtags:
                        total_hashtags[hashtag] += count
                    else:
                        total_hashtags[hashtag] = count

            return {'dates': response, 'resume': total_hashtags}

    def get_mencions(self, request):
        data = self.format_dates(request)
        if 'error' in data:
            error_message = data['error']
            return {'error': error_message}
        else:
            response = self.Data_base.process_data('USUARIOS')

            # Procesar los resultados de menciones para obtener la cantidad total
            total_mentions = {}
            for date_data in response.values():
                for mention, count in date_data.items():
                    if mention in total_mentions:
                        total_mentions[mention] += count
                    else:
                        total_mentions[mention] = count
            return {'dates': response, 'resume': total_mentions}

    def get_feelings(self, request):
        data = self.format_dates(request)

        if 'error' in data:
            error_message = data['error']
            return {'error': error_message}
        else:
            response = self.Data_base.process_data('SENTIMIENTOS')
            # Procesar los resultados de sentimientos para obtener la cantidad total
            total_sentiments = {'Negativo': 0, 'Neutro': 0, 'Positivo': 0}
            for date_data in response.values():
                for sentiment, count in date_data.items():
                    total_sentiments[sentiment] += count

            return {'dates': response, "resume": total_sentiments}

    def clear_db(self):
        self.Data_base.clear_all()