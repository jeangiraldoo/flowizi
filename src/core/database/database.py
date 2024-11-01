import sqlite3
from core.elements.environment import Environment
from core.elements.website import Website
from core.elements.file import File

conn = sqlite3.connect("example.db")
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON;")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS environments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        record INTEGER NOT NULL
)''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        url TEXT UNIQUE NOT NULL
)''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS websites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        url TEXT UNIQUE NOT NULL
)''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        url TEXT UNIQUE NOT NULL
)''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS environment_applications (
        environment_id INTEGER,
        element_id INTEGER,
        PRIMARY KEY (environment_id, element_id),
        FOREIGN KEY (environment_id) REFERENCES environments(id) ON DELETE CASCADE,
        FOREIGN KEY (element_id) REFERENCES applications(id) ON DELETE CASCADE
)''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS environment_websites (
        environment_id INTEGER,
        element_id INTEGER,
        PRIMARY KEY (environment_id, element_id),
        FOREIGN KEY (environment_id) REFERENCES environments(id) ON DELETE CASCADE,
        FOREIGN KEY (element_id) REFERENCES websites(id) ON DELETE CASCADE
)''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS environment_files (
        environment_id INTEGER,
        element_id INTEGER,
        PRIMARY KEY (environment_id, element_id),
        FOREIGN KEY (environment_id) REFERENCES environments(id) ON DELETE CASCADE,
        FOREIGN KEY (element_id) REFERENCES files(id) ON DELETE CASCADE
)''')


def add_environment(name):
    environment = (name, 0)
    try:
        cursor.execute("INSERT INTO environments (name, record) VALUES (?, ?)", environment)
        commit_changes()
        return True
    except:
        return False


def delete_environment(name):
    id = get_environment_ID(name)
    if not id:
        return False

    cursor.execute("DELETE FROM environments WHERE id = ?", (id,))
    commit_changes()


def insert_element(env_name, element_type, name, url):
    env_id = get_environment_ID(env_name)

    if not env_id:
        return False

    element_id = get_element_ID(name, element_type)

    if not element_id:
        element_id = insert_and_get_element_ID(name, url, element_type)

    insert_result = finish_insert_element(env_id, element_id, element_type)
    commit_changes()
    return insert_result


def delete_element(env_name, element_type, name):
    env_id = get_environment_ID(env_name)
    if not env_id:
        print("There is no environment with the specified name")
        return False

    element_id = get_element_ID(name, element_type)
    if not element_id:
        return False

    cursor.execute(f"DELETE FROM environment_{element_type} WHERE element_id = ?", (element_id,))
    commit_changes()
    return True


def get_environment_ID(env_name) -> int:
    try:
        cursor.execute("SELECT id FROM environments WHERE name = ?", (env_name,))
        env_result = cursor.fetchone()
        env_id = env_result[0]
        return env_id
    except:
        return 0


def get_element_ID(name, element_type) -> int:
    try:
        cursor.execute(f"SELECT id FROM {element_type} where name = ?", (name,))
        element_result = cursor.fetchone()
        element_id = element_result[0]
        return element_id
    except:
        return 0
 

def insert_and_get_element_ID(name, url, element_type) -> int:
    element = (name, url)
    cursor.execute(f"INSERT INTO {element_type} (name, url) VALUES (?, ?)", element)
    cursor.execute(f"SELECT id FROM {element_type} where name = ?", (name,))
    element_result = cursor.fetchone()
    element_id = element_result[0]

    return element_id


def finish_insert_element(env_id, element_id, element_type):
    try:
        cursor.execute(f"INSERT INTO environment_{element_type} (environment_id, element_id) VALUES (?, ?)", (env_id, element_id))
        return True
    except:
        return False


def update_environment_record(env_name, value):
    """Toogles the recording setting in an environment on or off"""
    try:
        cursor.execute("SELECT * FROM environments WHERE name = ?", (env_name,))
        environment = cursor.fetchone()
    except:
        print("The environment doesnt exist")

    record = environment[2]
    if record == value:
        print("The environment is already set not to be recorded")
    else:
        cursor.execute("UPDATE environments SET record = ? WHERE name = ?", (value, env_name))
        print("The record setting has been updated!")


def deserialize_elements():
    element_types = ["websites", "files"]
    environments = deserialize_environments()
    for i in range(len(element_types)):
        environments = deserialize_contained_elements(environments, element_types[i])
    return environments


def deserialize_environments():
    environments = []
    cursor.execute("SELECT * FROM environments")
    rows = cursor.fetchall()

    for tuple in rows:
        env = Environment(tuple[1])
        env.set_record(tuple[2])
        environments.append(env)

    return environments


def deserialize_contained_elements(envs, element_type):
    for environment in envs:
        env_id = get_environment_ID(environment.name)
        cursor.execute(f"SELECT element_id FROM environment_{element_type} WHERE environment_id = ?", (env_id,)) 
        result = cursor.fetchall()

        for tuple in result:
            cursor.execute(f"SELECT * FROM {element_type} WHERE id = ?", (tuple[0],))
            result = cursor.fetchone()
            element_list = getattr(environment, element_type)
            if element_type == "websites":
                new_element = Website(result[1], result[2])
            elif element_type == "files":
                new_element = File(result[1], result[2])
            else:
                new_element = Application(result[1], result[2])
            element_list.append(new_element)

    return envs

def commit_changes():
    conn.commit()
