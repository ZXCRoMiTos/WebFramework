from quopri import decodestring
from copy import deepcopy
from datetime import datetime


from patterns.behavioral import Observer, SmsNotifier, EmailNotifier
from patterns.architectural import DomainObject
from sqlite3 import connect
from hashlib import pbkdf2_hmac
from uuid import uuid1


def hash_password(salt, password):
    iterations = 10000
    return pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations).hex()


class User(DomainObject):
    auto_id = 1


class Guest(User):
    pass


class RegisteredUser(User):
    def __init__(self, login, name, password):
        self.id = User.auto_id
        User.auto_id += 1
        self.login = login
        self.name = name
        salt = self.login + self.name
        self.password = hash_password(salt, password)
        self.access_rights = 1


class VerifiedUser(User):
    pass


class UserFactory:
    types = {
        'guest': Guest,
        'registered_user': RegisteredUser,
        'verified_user': VerifiedUser,
    }

    @classmethod
    def create_user(cls, type_, *args):
        return cls.types[type_](*args)


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

    def __init__(self, name, category, content, user, date):
        self.id = Post.auto_id
        Post.auto_id += 1
        self.name = name
        self.category = category
        self.content = content
        self.creator = user
        self.date = date
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
    def create(cls, type_, *args):
        return cls.types[type_](*args)


class Comment(DomainObject):
    auto_id = 1

    def __init__(self, post_id, date, username, comment_text):
        self.id = Comment.auto_id
        Comment.auto_id += 1
        self.post_id = post_id
        self.date = date
        self.username = username
        self.comment_text = comment_text


class Engine:
    def __init__(self):
        self.registered_users = {}
        self.categories = {}
        self.subcategories = {}
        self.posts = {}
        self.comments = {}
        self.sessions = {}
        self.database_load()

    def database_load(self):
        self.get_categories()
        self.get_main_categories()
        self.get_subcategories()
        self.get_users()
        self.get_posts()
        self.get_comments()
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
            id, category_id, media_expansion, name, media, description, user_id, date = item
            category = self.find_category_by_id(category_id)
            content = [media, description]
            user = self.find_user_by_id(user_id)
            new_post = self.create_post(media_expansion, name, category, content, user, date)
            new_post.id = id
            self.posts[new_post.id] = new_post
            self.comments[new_post.id] = []

    def get_users(self):
        items = MapperRegistry.get_current_mapper('users').all()
        for item in items:
            id, login, name, password, access_rights = item
            new_user = self.create_user('registered_user', login, name, 'заглушка')
            new_user.password = password
            new_user.access_rights = access_rights
            self.registered_users[new_user.id] = new_user

    def get_comments(self):
        items = MapperRegistry.get_current_mapper('comments').all()
        for item in items:
            id, post_id, date, username, comment_text = item
            comment = self.create_comment(post_id, date, username, comment_text)
            comment.id = id
            self.comments[post_id].append(comment)

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
    def create_comment(*args):
        return Comment(*args)

    @staticmethod
    def get_date():
        return str(datetime.now()).split('.')[0]

    @staticmethod
    def get_page_of_posts(posts, page_number, page_size):
        return posts[(page_number-1)*page_size : (page_number)*page_size]

    def create_session(self, user):
        unique_id = str(uuid1())
        self.sessions[unique_id] = user
        return unique_id

    def check_user(self, email, password):
        for user in self.registered_users.values():
            if user.login == email:
                salt = email + user.name
                password = hash_password(salt, password)
                if user.password == password:
                    return user, True, ''
                return user, False, 'Неверный пароль'
            return None, False, 'Неверная почта'

    def get_session_id_for_user(self, user):
        for sessiond_id, user_in_sessions in self.sessions.items():
            if user_in_sessions == user:
                return sessiond_id
        return self.create_session(user)

    @staticmethod
    def create_user(type_, *args):
        return UserFactory.create_user(type_, *args)

    def find_user_by_id(self, id):
        if isinstance(id, int):
            try:
                return self.registered_users[id]
            except KeyError:
                raise Exception(f'Нет пользователя с id: {id}')
        raise Exception('Передан неверный тип данных, ожидается int')

    @staticmethod
    def create_category(type_, name):
        if isinstance(name, str):
            return CategoryFactory.create_category(type_, name)
        raise Exception('Передан неверный тип данных, ожидается str')

    def find_category_by_id(self, id):
        if isinstance(id, int):
            try:
                return self.categories[id]
            except KeyError:
                pass
            try:
                return self.subcategories[id]
            except KeyError:
                pass
            raise Exception(f'Нет категории с id: {id}')
        raise Exception('Передан неверный тип данных, ожидается int')

    @staticmethod
    def create_post(type_, name, category, content, user, date):
        if isinstance(name, str):
            if isinstance(category, CategoryBase):
                if isinstance(content, list):
                    return PostFactory.create(type_, name, category, content, user, date)
                raise Exception('Параметр content должен быть list')
            raise Exception('Параметр category должен быть CategoryBase')
        raise Exception('Параметр name должен быть str')

    def get_post_by_id(self, id):
        if isinstance(id, int):
            try:
                return self.posts[id]
            except KeyError:
                raise Exception(f'Нет категории с id: {id}')
        raise Exception('Передан неверный тип данных, ожидается int')

    @staticmethod
    def decode_value(val):
        if isinstance(val, str):
            val_b = bytes(val.replace('%', '=').replace('+', ' '), 'UTF-8')
            val_decode_str = decodestring(val_b)
            return val_decode_str.decode('UTF-8')
        raise Exception('Передан неверный тип данных, ожидается str')


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
        if isinstance(obj, ImagePost):
            media_expansion = 'image'
        elif isinstance(obj, GifPost):
            media_expansion = 'gif'
        query = f'INSERT INTO {self.table_name} (category_id, media_expansion, name, media, description, user_id, ' \
                f'create_date) VALUES (?, ?, ?, ?, ?, ?, ?);'
        self.cursor.execute(query, (obj.category.id, media_expansion, obj.name, obj.content[0], obj.content[1],
                                    obj.creator.id, obj.date))
        self.connection.commit()

    def update(self, obj):
        query = f'UPDATE {self.table_name} SET name = "{obj.name}", media = "{obj.content[0]}", ' \
                f'description = "{obj.content[1]}" WHERE id = {obj.id};'
        self.cursor.execute(query)
        self.connection.commit()


class CommentsMapper(BaseMapper):
    def __init__(self, connection):
        super().__init__(connection)
        self.table_name = 'comments'

    def create(self, obj):
        query = f'INSERT INTO {self.table_name} (post_id, date, username, comment_text) VALUES (?, ?, ?, ?);'
        self.cursor.execute(query, (obj.post_id, obj.date, obj.username, obj.comment_text))
        self.connection.commit()


class UsersMapper(BaseMapper):
    def __init__(self, connection):
        super().__init__(connection)
        self.table_name = 'users'

    def create(self, obj):
        query = f'INSERT INTO {self.table_name} VALUES (?, ?, ?, ?, ?);'
        self.cursor.execute(query, (obj.id, obj.login, obj.name, obj.password, obj.access_rights))
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
        'comments': CommentsMapper
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
        elif isinstance(obj, Comment):
            return CommentsMapper(con)

    @staticmethod
    def get_current_mapper(name):
        return MapperRegistry.mappers[name](con)


if __name__ == '__main__':
    con = connect('database/database.sql')
