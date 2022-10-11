from main.page_conroller import render
from patterns.creationals import Engine, Logger
from patterns.structural import route, Debug
from patterns.behavioral import FileWriter, ConsoleWriter, TemplateView, \
    ListView, CreateView, SmsNotifier, EmailNotifier, BaseSerializer
from datetime import date


site = Engine()
logger = Logger('main', FileWriter())


# осторожно, снизу временный код для создания категории и постов
def create_data():
    new_category = site.create_category('котики', None, [], [])
    new_category.notifiers.append(SmsNotifier())
    new_category.notifiers.append(EmailNotifier())
    site.categories.append(new_category)
    a_category = site.find_category_by_id(0)
    content = ['https://i.pinimg.com/originals/a0/1e/b9/a01eb920157d569f0c214bc48ef1dec4.jpg',
               'Красивый кот! И еще большой текст для просмотра переноса строки и отступа. ']
    new_post = site.create_post('image', 'Атос', a_category, content)
    site.posts.append(new_post)
    content = ['https://i.pinimg.com/originals/99/da/b9/99dab9d31ffc8b3b631d73f73005cd89.gif',
               'Проверка работы GIF, а также создания специального класса в фабрике. ']
    new_post = site.create_post('gif', 'Мяу', a_category, content)
    site.posts.append(new_post)
    new_user = site.create_user('registered_user', 'Петров')
    site.registered_users.append(new_user)
    new_category.subscribers.append(new_user)


create_data()
# все посты для главной страницы
posts = []
for item in site.categories:
    for itm in item.posts:
        posts.append(itm)


class Users(CreateView, ListView):
    template_name = 'users.html'

    def create_context_data(self):
        self.context['title'] = 'Пользователи'
        self.context['users'] = site.registered_users

    def create_object(self, data):
        name = data['name']
        name = site.decode_value(name)
        new_user = site.create_user('registered_user', name)
        site.registered_users.append(new_user)


@route('/')
class Index(ListView, CreateView):
    template_name = 'index.html'

    def create_context_data(self):
        self.context['title'] = 'Главная'
        self.context['categories_list'] = site.categories
        self.context['posts'] = site.posts

    def create_object(self, data):
        name = data['name']
        name = site.decode_value(name)
        category_id = data.get('category_id')

        category = None
        if category_id:
            category = site.find_category_by_id(int(category_id))

        new_category = site.create_category(name, category, [], [])
        new_category.notifiers.append(SmsNotifier)
        new_category.notifiers.append(EmailNotifier)
        logger.log('Создание категории')
        site.categories.append(new_category)


@route('/category/')
class Category(ListView, CreateView):
    template_name = 'category.html'

    def get_request_params(self, request):
        self.page_id = int(request['request_params']['id'])

    def create_context_data(self):
        category = site.find_category_by_id(self.page_id)
        self.category = category
        self.context['id'] = category.id
        self.context['name'] = category.name
        self.context['categories_list'] = category.subcategories
        self.context['posts_list'] = category.posts
        self.context['users_list'] = site.registered_users
        self.context['subscribers_list'] = category.subscribers

    def create_category(self, data):
        parents = self.category.parents
        parents.append(self.category.id)
        new_category = site.create_category(self.name, None, [], parents)
        new_category.notifiers.append(SmsNotifier)
        new_category.notifiers.append(EmailNotifier)
        self.category.subcategories.append(new_category)
        site.subcategories.append(new_category)

    def create_post(self, data):
        media = data['media']
        media = site.decode_value(media)
        media_expansion = media.split('.')[-1]

        if media_expansion != 'gif':
            media_expansion = 'image'

        description = data['description']
        description = site.decode_value(description)
        content = [media, description]
        logger.log('Создание поста')
        post = site.create_post(media_expansion, self.name, self.category, content)

        for category_id in self.category.parents:
            cat = site.find_category_by_id(category_id)
            cat.add_post(post)

        site.posts.append(post)
        posts.append(post)

    def edit_post(self, data):
        post_id = data['id']
        post = site.get_post_by_id(post_id)
        post.name = self.name
        media = data['media']
        description = data['description']
        content = [media, description]
        post.content = content

    def copy_post(self, data):
        post_id = data['id']
        old_post = site.get_post_by_id(post_id)
        if old_post:
            new_name = f'copy_{self.name}'
            new_post = old_post.clone()
            new_post.name = new_name
            logger.log('Копирование поста')
            site.posts.append(new_post)
            self.category.posts.append(new_post)

            for category_id in self.category.parents:
                cat = site.find_category_by_id(category_id)
                cat.posts.append(new_post)

            posts.append(new_post)

    def subscribe(self, data):
        user = site.find_user_by_name(self.name)
        self.category.subscribers.append(user)

    def create_object(self, data):
        request_types = {
            'create_category': self.create_category,
            'create_post': self.create_post,
            'edit_post': self.edit_post,
            'copy_post': self.copy_post,
            'subscribe': self.subscribe,
        }
        self.name = data['name']
        post_request_type = data['type']
        request_types[post_request_type](data)


@route('/api/')
class PostsApi:
    def __call__(self, request):
        return '200 OK', BaseSerializer(site.posts).save()