class DatabaseSchema:
    @staticmethod
    def init(cursor):
        DatabaseSchema._create_envs_table(cursor)
        DatabaseSchema._create_applications_table(cursor)
        DatabaseSchema._create_websites_table(cursor)
        DatabaseSchema._create_files_table(cursor)
        DatabaseSchema._create_envs_apps_table(cursor)
        DatabaseSchema._create_envs_websites_table(cursor)
        DatabaseSchema._create_envs_files_table(cursor)

    def _create_envs_table(cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS environments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                record INTEGER NOT NULL
        )''')

    def _create_applications_table(cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                url TEXT UNIQUE NOT NULL
        )''')

    def _create_websites_table(cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS websites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                url TEXT UNIQUE NOT NULL
        )''')

    def _create_files_table(cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                url TEXT UNIQUE NOT NULL
        )''')

    def _create_envs_apps_table(cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS environment_applications (
                environment_id INTEGER,
                element_id INTEGER,
                PRIMARY KEY (environment_id, element_id),
                FOREIGN KEY (environment_id) REFERENCES environments(id) ON DELETE CASCADE,
                FOREIGN KEY (element_id) REFERENCES applications(id) ON DELETE CASCADE
        )''')

    def _create_envs_websites_table(cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS environment_websites (
                environment_id INTEGER,
                element_id INTEGER,
                PRIMARY KEY (environment_id, element_id),
                FOREIGN KEY (environment_id) REFERENCES environments(id) ON DELETE CASCADE,
                FOREIGN KEY (element_id) REFERENCES websites(id) ON DELETE CASCADE
        )''')

    def _create_envs_files_table(cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS environment_files (
                environment_id INTEGER,
                element_id INTEGER,
                PRIMARY KEY (environment_id, element_id),
                FOREIGN KEY (environment_id) REFERENCES environments(id) ON DELETE CASCADE,
                FOREIGN KEY (element_id) REFERENCES files(id) ON DELETE CASCADE
        )''')
