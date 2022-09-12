class GetRequest:

    def __init__(self, enviour):
        self.query_string = enviour['QUERY_STRING']

    def process_incoming_data(self):
        result = {}
        if self.query_string:
            params = self.query_string.split('&')
            for param in params:
                key, value = param.split('=')
                result[key] = value
        return result

    def create_params_dict(self):
        return self.process_incoming_data()


class PostRequest:

    def __init__(self, enviour):
        data = enviour['CONTENT_LENGTH']
        self.content_length = int(data) if data else 0
        self.wsgi_input = enviour['wsgi.input']

    @staticmethod
    def process_incoming_data(data):
        result = {}
        if data:
            params = data.split('&')
            for param in params:
                key, value = param.split('=')
                result[key] = value
        return result

    def process_wsgi_incoming_data(self, data):
        result = {}
        if data:
            data_str = data.decode(encoding='utf-8')
            result = self.process_incoming_data(data_str)
        return result

    def get_reponse_wsgi_data(self):
        return self.wsgi_input.read(self.content_length) if self.content_length > 0 else b''

    def create_params_dict(self):
        data = self.get_reponse_wsgi_data()
        return self.process_wsgi_incoming_data(data)