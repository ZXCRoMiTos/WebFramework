from wsgiref.simple_server import make_server
from main.core import WebFramework
from urls import routes, fronts


application = WebFramework(routes, fronts)

with make_server('', 8080, application) as httpd:
    print('Сервер запущен на порту 8080...')
    httpd.serve_forever()
