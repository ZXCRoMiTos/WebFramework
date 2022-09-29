from quopri import decodestring
from copy import deepcopy


class User:
    pass


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
    def create(cls, type_):
        return cls.types[type_]()


class Category:
    auto_id = 0

    def __init__(self, name, category):
        self.id = Category.auto_id
        Category.auto_id += 1
        self.name = name
        self.category = category
        self.posts = []


class PostPrototype:
    def clone(self):
        return deepcopy(self)


class Post(PostPrototype):
    def __init__(self, name, category, content):
        self.name = name
        self.category = category
        self.content = content
        self.category.posts.append(self)


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
        self.guests = []
        self.registered_users = []
        self.verified_users = []
        self.categories = []
        self.posts = []

    @staticmethod
    def create_category(name, category=None):
        return Category(name, category)

    def find_category_by_id(self, id):
        for item in self.categories:
            if item.id == id:
                return item
        raise Exception(f'Нет категории с id: {id}')

    @staticmethod
    def create_post(type_, name, category, content):
        return PostFactory.create(type_, name, category, content)

    def get_post(self, name):
        for post in self.posts:
            if post.name == name:
                return post
        return None

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
    def __init__(self, name):
        self.name = name

    @staticmethod
    def log(text):
        print('log: ', text)
