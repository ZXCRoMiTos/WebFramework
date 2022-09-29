from datetime import date
from views import Index, Another, Category


def date_front(request):
    request['date'] = date.today()


fronts = [date_front]

routes = {
    '/': Index(),
    '/another/': Another(),
    '/category/': Category(),
}