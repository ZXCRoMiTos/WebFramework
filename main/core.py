class PageNotFound404:
    def __call__(self, request):
        return '404 PAGE NOT FOUND', '404 PAGE NOT FOUND'


class WebFramework:

    def __init__(self, routes, pages):
        self.routes = routes
        self.pages = pages

    def __call__(self, enviour, start_response):
        self.path = enviour['PATH_INFO']
        self.check_end_slash()
        self.choose_view()
        self.render_pages()
        return self.start(start_response)

    def check_end_slash(self):
        if not self.path.endswith('/'):
            self.path = f'{self.path}/'

    def choose_view(self):
        if self.path in self.routes:
            self.view = self.routes[self.path]
        else:
            self.view = PageNotFound404()

    def render_pages(self):
        self.request = {}
        for page in self.pages:
            page(self.request)

    def start(self, start_response):
        code, body = self.view(self.request)
        start_response(code, [('Content-Type', 'text/html')])
        return [body.encode('utf-8')]