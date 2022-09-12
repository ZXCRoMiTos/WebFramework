from main.page_conroller import render


class Index:
    def __call__(self, request):
        return '200 OK', render('index.html', date=request.get('date', None))


class Another:
    def __call__(self, request):
        return '200 OK', render('another.html', date=request.get('date', None))