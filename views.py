from main.page_conroller import render
from patterns.creationals import Engine, Logger
from patterns.structural import route, Debug


site = Engine()
logger = Logger('main')


# осторожно, снизу временный код для создания категории и постов
def create_category_and_post():
    new_category = site.create_category('котики', None, [], [])
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


@route('/')
class Index:

    """Класс главной страницы, на которой выводятся все посты и есть возможность создания категории"""

    @Debug('test for index')
    def __call__(self, request):

        if request['method'] == 'POST':

            # вся информация
            data = request['data']

            # имя из формы
            name = data['name']
            name = site.decode_value(name)

            # id категории из формы
            category_id = data.get('category_id')

            # None или получение существующей категории
            category = None
            if category_id:
                category = site.find_category_by_id(int(category_id))

            # создание новой категории
            new_category = site.create_category(name, category, [], [])

            # логирование
            logger.log('Создание категории')

            # добавление категории на сайт (на главную)
            site.categories.append(new_category)

        return '200 OK', render('index.html', date=request.get('date', None), posts=posts,  objects_list=site.categories)


@route('/category/')
class Category:

    """Класс категории, который отображает посты категории и дает возможность создания и копирования поста"""

    @Debug('test for category')
    def __call__(self, request):
        if request['method'] == 'POST':

            # вся информация
            data = request['data']

            # поле name, общее для всех форм
            name = data['name']
            name = site.decode_value(name)

            # текущая категория
            category = site.find_category_by_id(int(self.category_id))

            # создание поста
            if data['type'] == 'create_post':

                # получения медиа из запроса
                media = data['media']
                media = site.decode_value(media)
                media_expansion = media.split('.')[-1]

                # определение типа медиа
                if media_expansion != 'gif':
                    media_expansion = 'image'

                # описание для поста
                description = data['description']
                description = site.decode_value(description)

                # контент содержит в себе как медиа, так и описание
                content = [media, description]

                # логирование
                logger.log('Создание поста')

                # создание поста
                post = site.create_post(media_expansion, name, category, content)

                # итерирование по родителям, чтобы добавить пост и в них
                for category_id in category.parents:
                    cat = site.find_category_by_id(category_id)
                    cat.posts.append(post)

                # добавление поста на сайт
                site.posts.append(post)

                # добавление поста на главную страницу
                posts.append(post)

            # копирование поста
            elif data['type'] == 'copy_post':
                # получение поста для копирования
                old_post = site.get_post(name)
                if old_post:
                    # новое имя для поста-клона
                    new_name = f'copy_{name}'
                    # клонирование поста
                    new_post = old_post.clone()
                    # выдача нового имени
                    new_post.name = new_name

                    # логирование
                    logger.log('Копирование поста')

                    # добавление поста на сайт
                    site.posts.append(new_post)

                    # добавление поста в текущую категорию
                    category.posts.append(new_post)

                    # итерирование по родителям, чтобы добавить пост и в них
                    for category_id in category.parents:
                        cat = site.find_category_by_id(category_id)
                        cat.posts.append(new_post)

                    # добавление поста на главную
                    posts.append(new_post)

            elif data['type'] == 'create_subcategory':
                # генерация родителей для подкатегории
                parents = category.parents
                parents.append(category.id)
                # создание категории
                new_category = site.create_category(name, None, [], parents)
                # добавление подкатегории в текущую категорию
                category.subcategories.append(new_category)
                # добавление подкатегории на сайт
                site.subcategories.append(new_category)

            else:
                logger.log('Неизвестный пост запрос')

        try:
            # получение нужной категории о id
            self.category_id = int(request['request_params']['id'])
            category = site.find_category_by_id(int(self.category_id))

            return '200 OK', render('category.html',
                                    posts_list=category.posts,
                                    subcategories_list=category.subcategories,
                                    name=category.name,
                                    id=category.id)
        except KeyError:
            return '200 OK', 'No categories have been added yet'
