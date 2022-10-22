from jinja2 import FileSystemLoader
from jinja2.environment import Environment


def static(filename):
    static_path = 'static/'
    return static_path + filename


def templates(filename):
    templates_path = 'templates/'
    return templates_path + filename


def render(page_name, folder='pages', **kwargs):
    env = Environment()
    env.globals.update(zip=zip, static=static, template=templates)
    env.loader = FileSystemLoader(folder)
    template = env.get_template(page_name)
    return template.render(**kwargs)