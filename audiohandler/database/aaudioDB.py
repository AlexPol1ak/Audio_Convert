import sqlite3
from sqlite3 import Error
import asyncio
from .audioDB import AudioDB


# База данных аудиофайлов в виде базы данных SQLite. Включается в аудиоконвертере по установленному флагу.

class aopen_db():
    """Контекстный менеджер для соединения с базой данных"""

    def __init__(self, db_path: str):
        self.db: str = db_path

    async def __aenter__(self) -> sqlite3.Connection:
        """Соединение с базой данных."""

        self.conn: sqlite3.Connection = sqlite3.connect(self.db)

        return self.conn

    async def __aexit__(self, exc_type, exc_value, traceback) -> bool:
        """Закрытие соединения с базой данных."""

        await asyncio.sleep(1 / 10000)
        self.conn.close()

        return False



class aAudioDB(AudioDB):
    """База данных для хранения информации о конвертированных и оригинальных файлах."""

    def __init__(self, db_path: str = ""):
        """Инициализация базы данных."""
        super().__init__(db_path)

    async def ainsert_audio(self, audio_dict: dict) -> bool:
        """Записывает данные о конвертированном файле в базу данных."""

        query: str = f"""
                INSERT INTO
                audio (user_name, trek_name, original_format, path_original, path_convert, format, date)
                VALUES
                ("{audio_dict['user_name']}", "{audio_dict['trek_name']}",
                "{audio_dict['original_format']}", "{audio_dict['path_original']}",
                "{audio_dict['path_convert']}", "{audio_dict['format']}", "{audio_dict['date']}")"""

        async with aopen_db(self.database) as conn:
            try:
                cursor: sqlite3.Cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                print('Записан в бд', audio_dict['path_original'])
            except Error as e:
                print(e, 'execute_queryErorr')
        return True