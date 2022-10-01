from wsgiref.simple_server import make_server
from main.core import WebFramework, DebugApplication, FakeApplication
from urls import fronts
from patterns.structural import routes


application = WebFramework(routes, fronts)

with make_server('', 8080, application) as httpd:
    print('Сервер запущен на порту 8080...')
    httpd.serve_forever()
