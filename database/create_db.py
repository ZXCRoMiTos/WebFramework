import sqlite3


def execute_script(con, script):
    cursor = con.cursor()
    cursor.executescript(script)
    con.commit()
    print('Успешное выполнение скрипта')


connection = sqlite3.connect('database.sql')
with open('script.txt', 'r', encoding='utf-8') as file:
    script = file.read()

execute_script(connection, script)
connection.close()
