from datetime import date
from views import Index, Registration, Category, PostsApi, Login, Post
from patterns.structural import routes


def date_front(request):
    request['date'] = date.today()


fronts = [date_front]

add_routes = {
    '/registration/': Registration(),
}

for route in add_routes:
    routes[route] = add_routes[route]