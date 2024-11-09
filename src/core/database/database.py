import sqlite3
from core.system_detection.system_information import database_path
from core.elements.environment import Environment
from core.elements.website import Website
from core.elements.file import File
from core.elements.application import Application

conn = sqlite3.connect(database_path)
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


def add_environment(name: str):
    """Inserts an entry with a specific name into the environments table.

    The "record" attribute is set to 0 by default, indicating the environment
    will not be recorded.
    """
    env = (name, 0)
    query = "INSERT INTO environments (name, record) VALUES (?, ?)"
    cursor.execute(query, env)
    conn.commit()


def delete_environment(env_id: int):
    """Deletes an environment entry with a specific ID from
    the environments table.
    """
    query = "DELETE FROM environments WHERE id = ?"
    cursor.execute(query, (env_id,))
    conn.commit()


def insert_elem(elem_type: str, name: str, url: str) -> bool:
    """Inserts an entry into an element table.

    Args:
        elem_type (str): Element type ("websites", "applications" or "files").
        name (str): Name of the element to insert.
        url (str): URL or path of the element.
    Returns:
        bool: True if the element was successfully inserted.
              False if there's already an element with the same name or url.
    """
    try:
        elem = (name, url)
        query = f"INSERT INTO {elem_type} (name, url) VALUES (?, ?)"
        cursor.execute(query, elem)
        conn.commit()
        return True
    except:
        return False


def insert_env_elem(elem_type: str, env_id: int, elem_id: int) -> bool:
    """Inserts an entry into an environment_element table.

    This function is used when the user wants to add an element to a
    specific environment.

    Args:
        elem_type (str): Element type ("websites", "applications" or "files").
        env_id (int): ID of the environment to insert the element to.
        elem_id (str): ID of the element to insert.
    Returns:
        bool: True if the entry was successfully inserted.
              False if there's already an entry with the same env_id or elem_id.
    """
    try:
        query = f"INSERT INTO environment_{elem_type} (environment_id, element_id) VALUES (?, ?)"
        cursor.execute(query, (env_id, elem_id))
        conn.commit()
        return True
    except:
        return False


def delete_element(elem_type: str, env_id: int, elem_id: int):
    """Deletes an entry from an environment_element table.

    This function is used when the user wants to delete an element from a
    specific environment.

    Args:
        elem_type (str): Element type ("websites", "applications" or "files").
        env_id (int): ID of the environment.
        elem_id (int): ID of the element.
    """
    query = f"DELETE FROM environment_{elem_type} WHERE element_id = ? AND environment_id = ?"
    cursor.execute(query, (elem_id, env_id))
    conn.commit()


def get_element_ID(elem_type: str, name: str) -> int:
    """Returns the ID of a specific element.

    This function is used when an element/environment needs to be added or
    removed, as both the environment ID and element ID are required.

    Args:
        elem_type (str): The type of the element ("websites", "applications",
            or "files").
        name (str): The name of the element for which to retrieve the ID.

    Returns:
        int: The ID of the element, or 0 if no element is found with the given
        name.
    """
    try:
        query = f"SELECT id FROM {elem_type} where name = ?"
        cursor.execute(query, (name,))
        result = cursor.fetchone()
        id = result[0]
        return id
    except:
        return 0


def update_environment_record(env_name: str, value):
    """Toogles the recording setting in an environment on or off"""
    try:
        query = "SELECT * FROM environments WHERE name = ?"
        cursor.execute(query, (env_name,))
        environment = cursor.fetchone()
    except:
        print("The environment doesnt exist")

    record = environment[2]
    if record == value:
        print("The environment is already set not to be recorded")
    else:
        cursor.execute("UPDATE environments SET record = ? WHERE name = ?", (value, env_name))
        print("The record setting has been updated!")


def deserialize_elems() -> list[Environment]:
    """Deserializes all of the environments and their contained elements from
    the data in the database and returns a list with the resulting objects.
    """
    elem_types = ["websites", "files", "applications"]
    envs = deserialize_envs()
    for i in range(len(elem_types)):
        envs = deserialize_contained_elems(elem_types[i], envs)
    return envs


def deserialize_envs() -> list[Environment]:
    """Retrieves all of the entries in the environments table and creates
    an environment instance for each entry.

    Returns:
        list[Environment]: List of Environment instances.
    """
    environments = []
    query = "SELECT * FROM environments"
    cursor.execute(query)
    rows = cursor.fetchall()

    for tuple in rows:
        env = Environment(tuple[1])
        env.set_record(tuple[2])
        environments.append(env)

    return environments


def deserialize_contained_elems(elem_type: str, envs: list[Environment]) -> list[Environment]:
    """
    Deserializes elements associated with each environment and adds them
    to the corresponding attribute list in each "Environment" instance.

    Args:
        elem_type (str): Type of contained elements to deserialize (e.g., "websites").
        envs (list[Environment]): List of "Environment" instances to populate
        with the contained elements.

    Returns:
        list[Environment]: The same list of "Environment" instances, but with
        their corresponding element lists populated.
    """
    for environment in envs:
        env_id = get_element_ID("environments", environment.name)

        query = f"SELECT element_id FROM environment_{elem_type} WHERE environment_id = ?"
        cursor.execute(query, (env_id,))
        result = cursor.fetchall()

        for (elem_id,) in result:
            query = f"SELECT * FROM {elem_type} WHERE id = ?"
            cursor.execute(query, (elem_id,))
            id, name, url = cursor.fetchone()

            element_list = getattr(environment, elem_type)
            if elem_type == "websites":
                new_element = Website(name, url)
            elif elem_type == "files":
                new_element = File(name, url)
            else:
                new_element = Application(name, url)
            element_list.append(new_element)

    return envs
