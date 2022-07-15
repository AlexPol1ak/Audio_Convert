import sqlite3
from sqlite3 import Error

class DB():
    """База данных для хранения информации о конвертированных и оригинальных файлах."""
    
    def __init__(self, name_db = 'audioDB.sqlite', path_db="" ):
        self.conn = self.create_connection(name_db)
        self.create_table()


    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)
        return conn

    
    def execute_query(self,  query):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.conn.commit()
        except Error as e:
            print(e,'execute')
        return cursor

    def create_table(self):
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
        print(audio_dict)
        query = f"""
                INSERT INTO 
                audio (user_name, trek_name, original_format, path_original, path_convert, format, date)
                VALUES
                ("{audio_dict['user_name']}", "{audio_dict['trek_name']}", 
                "{audio_dict['original_format']}", "{audio_dict['path_original']}", 
                "{audio_dict['path_convert']}", "{audio_dict['format']}", "{audio_dict['date']}")"""
        self.execute_query(query)

