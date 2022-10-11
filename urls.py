from datetime import date
from views import Index, Users, Category, PostsApi
from patterns.structural import routes


def date_front(request):
    request['date'] = date.today()


fronts = [date_front]

add_routes = {
    '/users/': Users(),
}

for route in add_routes:
    routes[route] = add_routes[route]