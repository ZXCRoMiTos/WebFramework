from patterns.creationals import Engine, Logger, MapperRegistry
from patterns.structural import route, Debug
from patterns.behavioral import FileWriter, ConsoleWriter, TemplateView, \
    ListView, CreateView, SmsNotifier, EmailNotifier, BaseSerializer
from patterns.architectural import UnitOfWork


site = Engine()
logger = Logger('main', FileWriter())
UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistry)


class Users(CreateView, ListView):
    template_name = 'users.html'

    def create_context_data(self):
        self.context['title'] = 'Пользователи'
        self.context['users'] = site.registered_users.values()

    def create_object(self, data):
        name = data['name']
        name = site.decode_value(name)
        new_user = site.create_user('registered_user', name)
        site.registered_users[new_user.id] = new_user

        new_user.mark_create()
        UnitOfWork.get_current().commit()
        logger.log(f'Создан новый пользователь: id:{new_user.id}, name:{new_user.name}')


@route('/')
class Index(ListView, CreateView):
    template_name = 'index.html'

    def create_context_data(self):
        self.context['title'] = 'Главная'
        self.context['categories_list'] = site.categories.values()
        self.context['posts'] = site.posts.values()

    def create_object(self, data):
        name = data['name']
        name = site.decode_value(name)
        new_category = site.create_category('main_category', name)
        new_category.notifiers.append(SmsNotifier)
        new_category.notifiers.append(EmailNotifier)
        site.categories[new_category.id] = new_category
        new_category.mark_create()

        MapperRegistry.get_current_mapper('notifiers').create(new_category.id, 1, 1)
        UnitOfWork.get_current().commit()
        logger.log(f'Создание новой категории: id:{new_category.id}, name:{new_category.name}')


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
        self.context['users_list'] = site.registered_users.values()
        self.context['subscribers_list'] = category.subscribers
        self.context['parent'] = category.parent

    def create_category(self, data):
        name = data['name']
        new_category = site.create_category('subcategory', name)
        new_category.parent = self.category
        new_category.notifiers.append(SmsNotifier)
        new_category.notifiers.append(EmailNotifier)
        self.category.subcategories.append(new_category)
        site.subcategories[new_category.id] = new_category

        new_category.mark_create()
        MapperRegistry.get_current_mapper('notifiers').create(new_category.id, 1, 1)
        UnitOfWork.get_current().commit()
        logger.log(f'Создание новой категории: id:{new_category.id}, name:{new_category.name}')

    def create_post(self, data):
        name = data['name']
        media = data['media']
        media = site.decode_value(media)
        media_expansion = media.split('.')[-1]

        if media_expansion != 'gif':
            media_expansion = 'image'

        description = data['description']
        description = site.decode_value(description)
        content = [media, description]
        new_post = site.create_post(media_expansion, name, self.category, content)
        site.posts[new_post.id] = new_post

        new_post.mark_create()
        UnitOfWork.get_current().commit()
        logger.log(f'Создание нового поста: id:{new_post.id}, name:{new_post.name}')

    def edit_post(self, data):
        post_id = int(data['id'])
        name = data['name']
        post = site.get_post_by_id(post_id)
        post.name = name
        media = data['media']
        description = data['description']
        content = [media, description]
        post.content = content

        post.mark_update()
        UnitOfWork.get_current().commit()
        logger.log(f'Изменение поста: id:{post.id}, post:{post.name}')

    def copy_post(self, data):
        name = data['name']
        post_id = int(data['id'])
        old_post = site.get_post_by_id(post_id)
        if old_post:
            new_name = f'copy_{name}'
            new_post = old_post.clone()
            new_post.name = new_name
            site.posts[new_post.id] = new_post
            self.category.posts.append(new_post)

            new_post.mark_create()
            UnitOfWork.get_current().commit()
            logger.log(f'Копирование поста: id:{new_post.id}, post:{new_post.name}')

    def subscribe(self, data):
        user_id = int(data['id'])
        user = site.find_user_by_id(user_id)
        self.category.subscribers.append(user)

        MapperRegistry.get_current_mapper('subscribers').create(self.category.id, user.id)
        logger.log(f'Подписка пользователя id:{user.id}, name:{user.name} '
                   f'на категорию id:{self.category.id}, name:{self.category.name}')

    def create_object(self, data):
        request_types = {
            'create_category': self.create_category,
            'create_post': self.create_post,
            'edit_post': self.edit_post,
            'copy_post': self.copy_post,
            'subscribe': self.subscribe,
        }
        post_request_type = data['type']
        request_types[post_request_type](data)


@route('/api/')
class PostsApi:
    @Debug('API Post')
    def __call__(self, request):
        logger.log('Выдача API Post')
        return '200 OK', BaseSerializer(site.posts.values()).save()