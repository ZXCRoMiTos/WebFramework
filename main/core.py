from main.request_types import GetRequest, PostRequest
from quopri import decodestring


class PageNotFound404:
    def __call__(self, request):
        headers = []
        return '404 PAGE NOT FOUND', headers, '404 PAGE NOT FOUND'


class WebFramework:

    def __init__(self, routes, pages):
        self.routes = routes
        self.pages = pages
        self.request = {}

    def __call__(self, enviour, start_response):
        self.path = enviour['PATH_INFO']
        self.check_end_slash()
        self.check_request_type(enviour)
        self.check_cookie(enviour)
        self.choose_view()
        self.render_pages()
        return self.start(start_response)

    def check_end_slash(self):
        if not self.path.endswith('/'):
            self.path = f'{self.path}/'

    @staticmethod
    def decode_value(data):
        new_data = {}
        for key, value in data.items():
            new_key = bytes(key.replace('%', '=').replace('+', ' '), 'utf-8')
            decode_key = decodestring(new_key).decode('utf-8')
            new_value = bytes(value.replace('%', '=').replace('+', ' '), 'utf-8')
            decode_value = decodestring(new_value).decode('utf-8')
            new_data[decode_key] = decode_value
        return new_data

    def check_request_type(self, enviour):
        method = enviour['REQUEST_METHOD']
        self.request['method'] = method
        if method == 'POST':
            data = PostRequest(enviour).create_params_dict()
            value = self.decode_value(data)
            self.request['data'] = value
            print('Пришел POST запрос с параметрами:', value)
        if method == 'GET':
            data = GetRequest(enviour).create_params_dict()
            value = self.decode_value(data)
            if value:
                self.request['request_params'] = value
                print('Пришел GET запрос с параметрами:', value)

    def check_cookie(self, enviour):
        self.cookie = {}
        try:
            cookie = enviour['HTTP_COOKIE'].split()
            for item in cookie:
                try:
                    key, value = item.split('=')
                    self.cookie[key] = value
                except ValueError:
                    pass
        except KeyError:
            pass
        self.request['cookie'] = self.cookie

    def choose_view(self):
        if self.path in self.routes:
            self.view = self.routes[self.path]
        else:
            self.view = PageNotFound404()

    def render_pages(self):
        for page in self.pages:
            page(self.request)

    def start(self, start_response):
        code, new_headers, body = self.view(self.request)
        start_headers = [('Content-Type', 'text/html')]
        headers = start_headers + new_headers
        start_response(code, headers)
        return [body.encode('utf-8')]


class DebugApplication(WebFramework):

    def __init__(self, routes_obj, fronts_obj):
        self.application = WebFramework(routes_obj, fronts_obj)
        super().__init__(routes_obj, fronts_obj)

    def __call__(self, env, start_response):
        print('DEBUG MODE')
        print(env)
        return self.application(env, start_response)


class FakeApplication(WebFramework):

    def __init__(self, routes_obj, fronts_obj):
        self.application = WebFramework(routes_obj, fronts_obj)
        super().__init__(routes_obj, fronts_obj)

    def __call__(self, env, start_response):
        headers = []
        start_response('200 OK', headers, [('Content-Type', 'text/html')])
        return [b'Hello from Fake']
