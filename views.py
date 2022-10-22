from patterns.creationals import Engine, Logger, MapperRegistry
from patterns.structural import route, Debug
from patterns.behavioral import FileWriter, ConsoleWriter, TemplateView, \
    ListView, CreateView, SmsNotifier, EmailNotifier, BaseSerializer
from patterns.architectural import UnitOfWork


site = Engine()
logger = Logger('main', FileWriter())
UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistry)


class Registration(CreateView, ListView):
    template_name = 'register.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['title'] = 'Регистрация'
        return context

    def create_object(self, data):
        email = data['email']
        name = data['name']
        password = data['password1']
        new_user = site.create_user('registered_user', email, name, password)

        new_user.mark_create()
        UnitOfWork.get_current().commit()
        site.registered_users[new_user.id] = new_user
        session_id = site.create_session(new_user)
        self.headers.append(('Set-Cookie', f'session_id={session_id}; Path=/'))
        logger.log(f'Создание нового пользователя: id: {new_user.id}, name: {new_user.name}')


@route('/login/')
class Login(CreateView):
    template_name = 'login.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['title'] = 'Вход'
        try:
            context['msg'] = self.msg
            self.msg = ''
        except AttributeError:
            context['error_msg'] = ''
        return context

    def create_object(self, data):
        email = data['email']
        password = data['password']
        user, is_correct, error_msg = site.check_user(email, password)
        self.msg = error_msg
        if is_correct:
            self.msg = f'Здравствуйте, {user.name}'
            session_id = site.get_session_id_for_user(user)
            self.headers.append(('Set-Cookie', f'session_id={session_id}; Path=/'))


@route('/post/')
class Post(CreateView):
    template_name = 'post.html'

    def get_request_params(self, request):
        self.page_id = int(request['request_params']['id'])
        try:
            session_id = request['cookie']['session_id']
            user = site.sessions[session_id]
            self.user = user
        except KeyError:
            self.user = None

    def get_context_data(self):
        context = super().get_context_data()
        self.post = site.get_post_by_id(self.page_id)
        context['post'] = self.post
        context['user'] = self.user
        try:
            context['comments'] = site.comments[self.post.id]
        except KeyError:
            context['comments'] = []
        return context

    def create_object(self, data):
        if self.user:
            comment_text = data['comment']
            date = site.get_date()
            comment = site.create_comment(self.post.id, date, self.user.name, comment_text)
            site.comments[self.post.id].append(comment)

            comment.mark_create()
            UnitOfWork.get_current().commit()


@route('/')
class Index(ListView, CreateView):
    template_name = 'index.html'

    def get_request_params(self, request):
        try:
            session_id = request['cookie']['session_id']
            user = site.sessions[session_id]
            self.user = user
        except KeyError:
            self.user = None
        self.page_number = 1
        try:
            self.page_number = int(request['request_params']['page'])
            request['request_params'] = {}
        except KeyError:
            pass

    def get_context_data(self):
        context = super().get_context_data()
        posts = list(site.posts.values())
        page_size = 3
        context['title'] = 'Главная'
        context['categories_list'] = site.categories.values()
        context['posts'] = site.get_page_of_posts(posts, self.page_number, page_size)
        context['page_number'] = self.page_number
        context['last_page'] = len(posts) / page_size
        context['user'] = self.user
        return context

    def create_object(self, data):
        if self.user:
            name = data['name']
            name = site.decode_value(name)
            new_category = site.create_category('main_category', name)
            new_category.notifiers.append(SmsNotifier)
            new_category.notifiers.append(EmailNotifier)
            site.categories[new_category.id] = new_category
            new_category.mark_create()

            sms_notifier, email_notifier = 1, 1
            MapperRegistry.get_current_mapper('notifiers').create(new_category.id, sms_notifier, email_notifier)
            UnitOfWork.get_current().commit()
            logger.log(f'Создание новой категории: id:{new_category.id}, name:{new_category.name}')


@route('/category/')
class Category(ListView, CreateView):
    template_name = 'category.html'

    def get_request_params(self, request):
        try:
            session_id = request['cookie']['session_id']
            user = site.sessions[session_id]
            self.user = user
        except KeyError:
            self.user = None
        self.page_id = int(request['request_params']['id'])
        self.page_number = 1
        try:
            self.page_number = int(request['request_params']['page'])
            request['request_params'] = {'id': self.page_id}
        except KeyError:
            pass

    def get_context_data(self):
        context = super().get_context_data()
        category = site.find_category_by_id(self.page_id)
        posts = category.posts
        page_size = 3
        self.category = category
        context['title'] = 'Категория'
        context['id'] = category.id
        context['name'] = category.name
        context['categories_list'] = category.subcategories
        context['posts_list'] = site.get_page_of_posts(posts, self.page_number, page_size)
        context['users_list'] = site.registered_users.values()
        context['subscribers_list'] = category.subscribers
        context['parent'] = category.parent
        context['user'] = self.user
        context['page_id'] = self.page_id
        context['page_number'] = self.page_number
        context['last_page'] = len(posts) / page_size
        return context

    def create_category(self, data):
        name = data['name']
        new_category = site.create_category('subcategory', name)
        new_category.parent = self.category
        new_category.notifiers.append(SmsNotifier)
        new_category.notifiers.append(EmailNotifier)
        self.category.subcategories.append(new_category)
        site.subcategories[new_category.id] = new_category

        new_category.mark_create()
        sms_notifier, email_notifier = 1, 1
        MapperRegistry.get_current_mapper('notifiers').create(new_category.id, sms_notifier, email_notifier)
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
        date = site.get_date()
        new_post = site.create_post(media_expansion, name, self.category, content, self.user, date)
        site.posts[new_post.id] = new_post
        site.comments[new_post.id] = []

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
        self.category.subscribers.append(self.user)

        MapperRegistry.get_current_mapper('subscribers').create(self.category.id, self.user.id)
        logger.log(f'Подписка пользователя id:{self.user.id}, name:{self.user.name} '
                   f'на категорию id:{self.category.id}, name:{self.category.name}')

    def create_object(self, data):
        request_types = {
            'create_category': self.create_category,
            'create_post': self.create_post,
            'edit_post': self.edit_post,
            'copy_post': self.copy_post,
            'subscribe': self.subscribe,
        }
        if self.user:
            post_request_type = data['type']
            request_types[post_request_type](data)


def hide_information(item):
    item.category = item.category.name
    item.creator = item.creator.name
    return item


@route('/api/')
class PostsApi:
    @Debug('API Post')
    def __call__(self, request):
        headers = []
        result = []
        for item in site.posts.values():
            new_item = {}
            new_item['id'] = item.id
            new_item['name'] = item.name
            new_item['category'] = item.category.name
            new_item['content'] = item.content
            new_item['creator'] = item.creator.name
            result.append(new_item)
        return '200 OK', headers, BaseSerializer(result).save()