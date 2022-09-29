from main.page_conroller import render
from patterns.creationals import Engine, Logger


site = Engine()
logger = Logger('main')


# осторожно, снизу временный код для создания категории и постов
def create_category_and_post():
    new_category = site.create_category('котики', None)
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


create_category_and_post()
# все посты для главной страницы
posts = []
for item in site.categories:
    for itm in item.posts:
        posts.append(itm)


class Another:
    def __call__(self, request):
        return '200 OK', render('another.html', date=request.get('date', None))


class Index:

    """Класс главной страницы, на которой выводятся все посты и есть возможность создания категории"""

    def __call__(self, request):

        if request['method'] == 'POST':

            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category_id = data.get('category_id')

            category = None
            if category_id:
                category = site.find_category_by_id(int(category_id))

            new_category = site.create_category(name, category)

            logger.log('Создание категории')
            site.categories.append(new_category)

        return '200 OK', render('index.html', date=request.get('date', None), posts=posts,  objects_list=site.categories)


class Category:

    """Класс категории, который отображает посты категории и дает возможность создания и копирования поста"""

    category_id = -1

    def __call__(self, request):
        if request['method'] == 'POST':

            data = request['data']
            name = data['name']
            name = site.decode_value(name)

            category = site.find_category_by_id(int(self.category_id))

            if data['type'] == 'create_post':

                media = data['media']
                media = site.decode_value(media)
                media_expansion = media.split('.')[-1]

                if media_expansion != 'gif':
                    media_expansion = 'image'

                description = data['description']
                description = site.decode_value(description)

                content = [media, description]

                if self.category_id != -1:
                    logger.log('Создание поста')
                    post = site.create_post(media_expansion, name, category, content)
                    site.posts.append(post)
                    posts.append(post)

            elif data['type'] == 'copy_post':
                old_post = site.get_post(name)
                if old_post:
                    new_name = f'copy_{name}'
                    new_post = old_post.clone()
                    new_post.name = new_name
                    logger.log('Копирование поста')
                    site.posts.append(new_post)
                    category.posts.append(new_post)
                    posts.append(new_post)

            else:
                logger.log('Неизвестный пост запрос')

        try:
            self.category_id = int(request['request_params']['id'])
            category = site.find_category_by_id(int(self.category_id))

            return '200 OK', render('category.html',
                                    objects_list=category.posts,
                                    name=category.name,
                                    id=category.id)
        except KeyError:
            return '200 OK', 'No categories have been added yet'
