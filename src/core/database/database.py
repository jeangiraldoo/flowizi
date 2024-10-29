import sqlite3

conn = sqlite3.connect("example.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS environments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        record INTEGER NOT NULL
    )
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        url TEXT UNIQUE NOT NULL
        )
    CREATE TABLE IF NOT EXISTS websites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        url TEXT UNIQUE NOT NULL
        )
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        url TEXT UNIQUE NOT NULL
        )
    CREATE TABLE IF NOT EXISTS environment_applications (
        environment_id INTEGER,
        application_id INTEGER,
        PRIMARY KEY (environment_id, project_id),
        FOREIGN KEY (environment_id) REFERENCES environments(id) ON DELETE CASCADE,
        FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
        )
    CREATE TABLE IF NOT EXISTS environment_websites (
        environment_id INTEGER,
        website_id INTEGER,
        PRIMARY KEY (environment_id, project_id),
        FOREIGN KEY (environment_id) REFERENCES environments(id) ON DELETE CASCADE,
        FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE
        )
    CREATE TABLE IF NOT EXISTS environment_files (
        environment_id INTEGER,
        file_id INTEGER,
        PRIMARY KEY (environment_id, file_id),
        FOREIGN KEY (environments_id) REFERENCES environments(id) ON DELETE CASCADE,
        FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
    )
''')


def add_environment(name):
    environment = (name, 0)
    try:
        cursor.execute("INSERT INTO environments (name, record) VALUES (?, ?)", environment)
        print(f"The {name} environment was successfully created!")
    except:
        print("Error. There's already an environment with that name.")


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


conn.commit()
