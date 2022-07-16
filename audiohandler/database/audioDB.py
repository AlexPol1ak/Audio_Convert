import sqlite3
from sqlite3 import Error

# База данных аудиофайлов в виде базы данных SQLite. Включается в аудиоконвертере по установленному флагу.

class AudioDB():
    """База данных для хранения информации о конвертированных и оригинальных файлах."""
    
    def __init__(self, db_path="" ):
        """Инициализация базы данных."""

        self.name = 'audio.sqlite'

        # Если путь не задан, то база данных будет лежать в папке с программой.
        self.conn = self.create_connection(db_file=self.name, path=db_path)
        # Создаем таблицу в базе данных.
        self.create_table()


    def create_connection(self, db_file, path=''):
        """ Создает соединение с базой данных. """

        # Если бд не существует, то создаем ее.
        if path != '':
            db_file = path + '/' + db_file

        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)
        return conn

    
    def execute_query(self,  query):
        """Выполняет запрос к базе данных."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.conn.commit()
        except Error as e:
            print(e,'execute_queryErorr')
        return cursor


    def create_table(self):
        """Создает таблицу в базе данных если не существует."""
        query = """CREATE TABLE IF NOT EXISTS audio (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_name TEXT,
                            trek_name TEXT,
                            original_format TEXT,
                            path_original TEXT,
                            path_convert TEXT,
                            format TEXT,
                            date TEXT
                            )"""
        self.execute_query(query)


    def insert_audio(self, audio_dict):
        """Вставляет данные о конвертированном файле в базу данных."""

        query = f"""
                INSERT INTO 
                audio (user_name, trek_name, original_format, path_original, path_convert, format, date)
                VALUES
                ("{audio_dict['user_name']}", "{audio_dict['trek_name']}", 
                "{audio_dict['original_format']}", "{audio_dict['path_original']}", 
                "{audio_dict['path_convert']}", "{audio_dict['format']}", "{audio_dict['date']}")"""
        self.execute_query(query)

