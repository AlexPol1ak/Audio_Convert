import os
import sqlite3
from sqlite3 import Error


# База данных аудиофайлов в виде базы данных SQLite. Включается в аудиоконвертере по установленному флагу.

class open_db():
    """Контекстный менеджер для соединения с базой данных"""

    def __init__(self,db_path :str):
        self.db :str = db_path

    def __enter__(self) ->sqlite3.Connection:
        """Соединение с базой данных."""

        self.conn :sqlite3.Connection = sqlite3.connect(self.db)

        return self.conn

    def __exit__(self, exc_type, exc_value, traceback)->bool:
        """Закрытие соединения с базой данных."""

        self.conn.close()

        return False


class AudioDB():
    """База данных для хранения информации о конвертированных и оригинальных файлах."""
    
    def __init__(self, db_path :str = ""):
        """Инициализация базы данных."""

        # Имя базы данных.
        self.name :str= 'audio.sqlite'
        # Путь к базе данных.
        self.db_path :str= db_path
        # Создаем базу данных, если ее нет, вставляем таблицу, и возвращаем путь к ней.
        self.database :str= self.create_db(db_name=self.name, path=self.db_path)


    def create_db(self, db_name :str, path:str = '') ->str:
        """Создает базу данных, создает таблицу для хранения информации о аудио, возвращает путь к базе данных."""

        if path != '':
              db_name = os.path.join(path, db_name)

        db :str = self.create_table(db=db_name)
        return db


    def create_table(self,db :str)->str:
        """Создает таблицу в базе данных если ее не существует."""

        query :str = """CREATE TABLE IF NOT EXISTS audio (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_name TEXT,
                            trek_name TEXT,
                            original_format TEXT,
                            path_original TEXT,
                            path_convert TEXT,
                            format TEXT,
                            date DateTime,
                            original_size_b INT,
                            original_size_mb FLOAT,
                            convert_size_b INT,
                            convert_size_mb FLOAT
                            )"""

        with open_db(db) as conn:
            try:
                cursor :sqlite3.Cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
            except Error as e:
                print(e, 'execute_queryErorr')
        return db


    def insert_audio(self, audio_dict :dict)->bool:
        """Записывает данные о конвертированном файле в базу данных."""

        query :str = f"""
                INSERT INTO
                audio (user_name, trek_name, original_format, path_original, path_convert, format, date,
                original_size_b, original_size_mb, convert_size_b, convert_size_mb )
                VALUES
                ("{audio_dict['user_name']}", "{audio_dict['trek_name']}",
                "{audio_dict['original_format']}", "{audio_dict['path_original']}",
                "{audio_dict['path_convert']}", "{audio_dict['format']}", "{audio_dict['date']}",
                "{audio_dict['original_size_b']}", "{audio_dict['original_size_mb']}","{audio_dict['convert_size_b']}",
                "{audio_dict['convert_size_mb']}"
                )"""

        with open_db(self.database) as conn:
            try:
                cursor :sqlite3.Cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
            except Error as e:
                print(e, 'execute_queryErorr')

        return True

