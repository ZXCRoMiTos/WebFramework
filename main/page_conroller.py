from jinja2 import FileSystemLoader
from jinja2.environment import Environment


def render(page_name, folder='pages', **kwargs):
    env = Environment()
    env.globals.update(zip=zip)
    env.loader = FileSystemLoader(folder)
    template = env.get_template(page_name)
    return template.render(**kwargs)