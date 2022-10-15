import sqlite3


def execute_script(con, script):
    cursor = con.cursor()
    cursor.executescript(script)
    con.commit()
    print('Успешное выполнение скрипта')


connection = sqlite3.connect('database.sql')

create_categories_table = """
DROP TABLE IF EXISTS categories;
CREATE TABLE IF NOT EXISTS categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL
);

DROP TABLE IF EXISTS main_categories;
CREATE TABLE IF NOT EXISTS main_categories (
    id INTEGER PRIMARY KEY
);

DROP TABLE IF EXISTS subcategories;
CREATE TABLE IF NOT EXISTS subcategories (
  parent_id INT NOT NULL,
  child_id INT NOT NULL,
  PRIMARY KEY (parent_id, child_id),
  CONSTRAINT fk_parent_id FOREIGN KEY (parent_id) REFERENCES categories (id),
  CONSTRAINT fk_child_id FOREIGN KEY (child_id) REFERENCES categories (id)
);

DROP TABLE IF EXISTS posts;
CREATE TABLE IF NOT EXISTS posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  category_id INTEGER,
  media_expansion TEXT NOT NULL,
  name TEXT NOT NULL,
  media TEXT NOT NULL,
  description TEXT NOT NULL,
  FOREIGN KEY (category_id) REFERENCES categories (id)
);

DROP TABLE IF EXISTS users;
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

DROP TABLE IF EXISTS subscribers;
CREATE TABLE IF NOT EXISTS subscribers (
  category_id INT NOT NULL,
  user_id INT NOT NULL,
  PRIMARY KEY (category_id, user_id),
  CONSTRAINT fk_category_id FOREIGN KEY (category_id) REFERENCES categories (id),
  CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users (id)
);

DROP TABLE IF EXISTS notifiers;
CREATE TABLE IF NOT EXISTS notifiers (
  category_id INTEGER PRIMARY KEY,
  sms INT NOT NULL,
  email INT NOT NULL,
  FOREIGN KEY (category_id) REFERENCES categories (id)
);
"""

execute_script(connection, create_categories_table)
connection.close()
