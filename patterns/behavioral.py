from jsonpickle import dumps, loads
from datetime import datetime
import sys
sys.path.append('../')
from main.page_conroller import render


class FileWriter:
    def write(self, text):
        now = datetime.now()
        with open(f'logs/{now.year}-{now.month}-{now.day}.txt', 'a', encoding='utf-8') as file:
            file.write(f'{text}\n')


class ConsoleWriter:
    @staticmethod
    def write(text):
        print(text)


class TemplateView:
    template_name = 'template.html'

    def get_context_data(self):
        return {}

    def get_template(self):
        return self.template_name

    def render_template_with_context(self):
        template_name = self.get_template()
        contex = self.get_context_data()
        return '200 OK', render(template_name, **contex)

    def __call__(self, request):
        return self.render_template_with_context()


class ListView(TemplateView):
    queryset = []
    context_object_name = 'objects_list'
    context = {context_object_name: queryset}

    def get_context_data(self):
        return self.context


class CreateView(TemplateView):

    @staticmethod
    def get_request_data(request):
        return request['data']

    def get_request_params(self, request):
        pass

    def create_object(self, data):
        pass

    def create_context_data(self):
        pass

    def __call__(self, request):
        self.get_request_params(request)
        self.create_context_data()
        if request['method'] == 'POST':
            data = self.get_request_data(request)
            self.create_object(data)
            return self.render_template_with_context()
        else:
            return super().__call__(request)


class Observer:
    def __init__(self):
        self.notifiers = []

    def notify(self, post_name):
        for alert in self.notifiers:
            for user in self.subscribers:
                alert.notify(user, self.name, post_name)


class SmsNotifier:
    @staticmethod
    def notify(user, category_name, post_name):
        print(f'SMS: Для {user.name}: В категории {category_name} новый пост - {post_name}!')


class EmailNotifier:
    @staticmethod
    def notify(user, category_name, post_name):
        print(f'EMAIL: Для {user.name}: В категории {category_name} новый пост - {post_name}!')


class BaseSerializer:
    def __init__(self, objects):
        self.objects = objects

    def save(self):
        return dumps(self.objects)

    @staticmethod
    def load(data):
        return loads(data)
