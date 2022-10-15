from quopri import decodestring
from copy import deepcopy
from datetime import datetime
from patterns.behavioral import Observer, SmsNotifier, EmailNotifier
from patterns.architectural import DomainObject
from sqlite3 import connect


class User(DomainObject):
    auto_id = 0

    def __init__(self, name):
        self.id = User.auto_id
        self.name = name
        User.auto_id += 1


class Guest(User):
    pass


class RegisteredUser(User):
    pass


class VerifiedUser(User):
    pass


class UserFactory:
    types = {
        'guest': Guest,
        'registered_user': RegisteredUser,
        'verified_user': VerifiedUser,
    }

    @classmethod
    def create_user(cls, type_, name):
        return cls.types[type_](name)


class CategoryBase(Observer, DomainObject):
    auto_id = 0

    def __init__(self, name):
        self.id = CategoryBase.auto_id
        CategoryBase.auto_id += 1
        self.name = name
        self.subcategories = []
        self.parent = None
        self.posts = []
        self.subscribers = []
        super().__init__()

    def add_post(self, post):
        self.posts.append(post)
        if self.parent:
            self.parent.add_post(post)
        self.notify(post.name)


class Category(CategoryBase):
    pass


class Subcategory(CategoryBase):
    pass


class MainCategory(CategoryBase):
    pass


class CategoryFactory:
    types = {
        'category': Category,
        'subcategory': Subcategory,
        'main_category': MainCategory,
    }

    @classmethod
    def create_category(cls, type_, name):
        return cls.types[type_](name)


class PostPrototype:
    def clone(self):
        return deepcopy(self)


class Post(PostPrototype, DomainObject):
    auto_id = 1

    def __init__(self, name, category, content):
        self.id = Post.auto_id
        Post.auto_id += 1
        self.name = name
        self.category = category
        self.content = content
        self.category.add_post(self)


class ImagePost(Post):
    pass


class GifPost(Post):
    pass


class PostFactory:
    types = {
        'image': ImagePost,
        'gif': GifPost,
    }

    @classmethod
    def create(cls, type_, name, category, content):
        return cls.types[type_](name, category, content)


class Engine:
    def __init__(self):
        self.registered_users = {}
        self.categories = {}
        self.subcategories = {}
        self.posts = {}
        self.database_load()

    def database_load(self):
        self.get_categories()
        self.get_main_categories()
        self.get_subcategories()
        self.get_posts()
        self.get_users()
        self.get_subscribers()
        self.get_notifiers()

    def get_categories(self):
        items = MapperRegistry.get_current_mapper('category').all()
        for item in items:
            id, name = item
            new_category = self.create_category('category', name)
            new_category.id = id
            self.subcategories[new_category.id] = new_category

    def get_subcategories(self):
        subcategories = MapperRegistry.get_current_mapper('subcategory').all()
        for subcategory in subcategories:
            parent_id, child_id = subcategory
            parent_category = self.find_category_by_id(parent_id)
            child_category = self.find_category_by_id(child_id)
            child_category.parent = parent_category
            parent_category.subcategories.append(child_category)

    def get_main_categories(self):
        main_categories = MapperRegistry.get_current_mapper('main_category').all()
        for item in main_categories:
            id = item[0]
            category = self.find_category_by_id(id)
            self.categories[category.id] = category

    def get_posts(self):
        items = MapperRegistry.get_current_mapper('posts').all()
        for item in items:
            id, category_id, media_expansion, name, media, description = item
            category = self.find_category_by_id(category_id)
            content = [media, description]
            new_post = self.create_post(media_expansion, name, category, content)
            new_post.id = id
            self.posts[new_post.id] = new_post

    def get_users(self):
        items = MapperRegistry.get_current_mapper('users').all()
        for item in items:
            id, name = item
            new_user = self.create_user('registered_user', name)
            new_user.id = id
            self.registered_users[new_user.id] = new_user

    def get_subscribers(self):
        items = MapperRegistry.get_current_mapper('subscribers').all()
        for item in items:
            category_id, user_id = item
            category = self.find_category_by_id(category_id)
            user = self.find_user_by_id(user_id)
            category.subscribers.append(user)

    def get_notifiers(self):
        items = MapperRegistry.get_current_mapper('notifiers').all()
        for item in items:
            category_id, sms, email = item
            category = self.find_category_by_id(category_id)
            if sms:
                category.notifiers.append(SmsNotifier())
            if email:
                category.notifiers.append(EmailNotifier())

    @staticmethod
    def create_user(type_, name):
        return UserFactory.create_user(type_, name)

    def find_user_by_id(self, id):
        if id in self.registered_users:
            return self.registered_users[id]
        raise Exception(f'Нет пользователя с id: {id}')

    @staticmethod
    def create_category(type_, name):
        return CategoryFactory.create_category(type_, name)

    def find_category_by_id(self, id):
        if id in self.categories:
            return self.categories[id]
        elif id in self.subcategories:
            return self.subcategories[id]
        raise Exception(f'Нет категории с id: {id}')

    @staticmethod
    def create_post(type_, name, category, content):
        return PostFactory.create(type_, name, category, content)

    def get_post_by_id(self, id):
        if id in self.posts:
            return self.posts[id]
        raise Exception(f'Нет категории с id: {id}')

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace('+', ' '), 'UTF-8')
        val_decode_str = decodestring(val_b)
        return val_decode_str.decode('UTF-8')


class SingletonByName(type):
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instanse = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instanse:
            return cls.__instanse['name']
        else:
            cls.__instanse[name] = super().__call__(*args, **kwargs)
            return cls.__instanse[name]


class Logger(metaclass=SingletonByName):
    def __init__(self, name, writer):
        self.name = name
        self.writer = writer

    def log(self, text):
        self.writer.write(f'{datetime.now()}: {text}')


class BaseMapper:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.table_name = 'basename'

    def all(self):
        query = f"SELECT * FROM {self.table_name};"
        items = self.cursor.execute(query)
        return items


class CategoryMapper(BaseMapper):
    def __init__(self, connection):
        super().__init__(connection)
        self.table_name = 'categories'

    def create(self, obj):
        query = f"INSRT INTO {self.table_name} (name) VALUES ('{obj.name}');"
        self.cursor.execute(query)
        self.connection.commit()


class MainCategoryMapper(BaseMapper):
    def __init__(self, connection):
        super().__init__(connection)
        self.table_name = 'main_categories'

    def create(self, obj):
        script = f'INSERT INTO {self.table_name} VALUES ({obj.id});' \
                 f'INSERT INTO categories VALUES ({obj.id}, "{obj.name}");'
        self.cursor.executescript(script)
        self.connection.commit()


class SubcategoryMapper(BaseMapper):
    def __init__(self, connection):
        super().__init__(connection)
        self.table_name = 'subcategories'

    def create(self, obj):
        script = f'INSERT INTO {self.table_name} VALUES ({obj.parent.id}, {obj.id});' \
                 f'INSERT INTO categories VALUES ({obj.id}, "{obj.name}");'
        self.cursor.executescript(script)
        self.connection.commit()


class PostsMapper(BaseMapper):
    def __init__(self, connection):
        super().__init__(connection)
        self.table_name = 'posts'

    def create(self, obj):
        query = f'INSERT INTO {self.table_name} (category_id, media_expansion, name, media, description) ' \
                f'VALUES ({obj.category.id}, "image", "{obj.name}", "{obj.content[0]}", "{obj.content[1]}");'
        self.cursor.execute(query)
        self.connection.commit()

    def update(self, obj):
        query = f'UPDATE {self.table_name} SET name = "{obj.name}", media = "{obj.content[0]}", ' \
                f'description = "{obj.content[1]}" WHERE id = {obj.id};'
        self.cursor.execute(query)
        self.connection.commit()


class UsersMapper(BaseMapper):
    def __init__(self, connection):
        super().__init__(connection)
        self.table_name = 'users'

    def create(self, obj):
        query = f'INSERT INTO {self.table_name} (id, name) VALUES ("{obj.id}", "{obj.name}");'
        self.cursor.execute(query)
        self.connection.commit()


class SubcribersMapper(BaseMapper):
    def __init__(self, connection):
        super().__init__(connection)
        self.table_name = 'subscribers'

    def create(self, category_id, user_id):
        query = f'INSERT INTO {self.table_name} VALUES ("{category_id}", "{user_id}");'
        self.cursor.execute(query)
        self.connection.commit()


class NotifiersMapper(BaseMapper):
    def __init__(self, connection):
        super().__init__(connection)
        self.table_name = 'notifiers'

    def create(self, category_id, sms, email):
        query = f'INSERT INTO {self.table_name} VALUES ({category_id}, {sms}, {email});'
        self.cursor.execute(query)
        self.connection.commit()


class MapperRegistry:
    mappers = {
        'category': CategoryMapper,
        'subcategory': SubcategoryMapper,
        'main_category': MainCategoryMapper,
        'posts': PostsMapper,
        'users': UsersMapper,
        'subscribers': SubcribersMapper,
        'notifiers': NotifiersMapper,
    }

    @staticmethod
    def get_mapper(obj):
        if isinstance(obj, Subcategory):
            return SubcategoryMapper(con)
        elif isinstance(obj, MainCategory):
            return MainCategoryMapper(con)
        elif isinstance(obj, Category):
            return CategoryMapper(con)
        elif isinstance(obj, Post):
            return PostsMapper(con)
        elif isinstance(obj, RegisteredUser):
            return UsersMapper(con)

    @staticmethod
    def get_current_mapper(name):
        return MapperRegistry.mappers[name](con)


con = connect('database/database.sql')