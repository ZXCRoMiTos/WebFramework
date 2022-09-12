from jinja2 import Template
from os.path import join


def render(page_name, folder='pages', **kwargs):
    file_path = join(folder, page_name)
    with open(file_path, encoding='utf-8') as file:
        page = Template(file.read())
    return page.render(**kwargs)