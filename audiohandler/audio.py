# Импорт функции подключения кодека ffmpeg
from .codecsetting import connect_ffmpeg
connect_ffmpeg()

# Импорт класс для создания базы данных
from .database.audioDB import AudioDB

from pydub import AudioSegment
import os
import shutil
from datetime import datetime
import subprocess



class AudioConverter():
    """Аудио конвертер."""

    number_converters = 0 # Количество объектов класса
    number_db = 0 # Количество баз данных
    formats: list[str] = ['ac3', 'asf', 'Flac', 'mp3', 'mp4', 'mov', "ogg", 'wav', ]  # '-AAC' '-DTS' '-wma'

    def __init__(self, setting_dict :dict = None):
        """Инициализация настроек конвертора."""

        self.storage_path :str = '' # путь к директории для хранения оригинальных и конвертируемых треков
        self.move :bool = False # перемещать оригинальные треки в директорию оригиналов

        self.db = None # База данных
        self.wirte_db = False # Включить запись в бд ,если флаг включен

        # Устнановка настроек со словаря.
        self.install_settings(setting_dict)
        # Создание директорий для хранения треков если их не существует
        self.storage_dirs :dict = self.create_storage_dirs() # пути к директориям для хранения треков
        # Количество объектов класса

        AudioConverter.number_converters += 1

    def __repr__(self):
        """Возвращает строку описания объекта."""
        return 'audiohandler.audio.AudioConverter() object'


    def install_settings(self, sett_dict :dict) ->None:
        """Установка настроек конвертора."""
        # Разбор словря с настройками и установка их в класс

        if isinstance(sett_dict, dict):

            # Установка пути к директории для хранения треков, если он указан и существует
            path = sett_dict.get('storage_path', '')
            if os.path.exists(path):
                self.storage_path = path

            # Установка флага перемещения оригинальных треков
            move = sett_dict.get('move', False)
            if isinstance(move, bool):
                self.move = move

            # Установка флага записи в базу данных. Установка пути к базе данных если указан и существует.
            # Создание базы данных если она не существует.
            write_db = sett_dict.get('write_db', False)
            if isinstance(write_db, bool) and write_db == True:
                self.wirte_db = True

                db_path = sett_dict.get('db_path', '')
                if os.path.exists(db_path):
                    # Создание базы данных в указаной директории
                    self.db = AudioDB(db_path = db_path)
                    AudioConverter.number_db += 1

                else:
                    # Создание базы данных в директории по умолчанию.
                    self.db = AudioDB()
                    AudioConverter.number_db += 1


    def create_storage_dirs(self) -> dict :
        """Создает директории для хранения оригинальных и конвертируемых треков."""

        dir_original = 'original_tracks'
        dir_convert = 'convertible_tracks'

        # Если укзан путь- дериктории для хранения треков создаются по указанному пути
        if self.storage_path != '' and os.path.exists(self.storage_path):
            # dir_original = self.storage_path + '/' + dir_original
            # dir_convert = self.storage_path + '/' + dir_convert
            dir_original = os.path.join(self.storage_path, dir_original)
            dir_convert = os.path.join(self.storage_path, dir_convert)

        # Создает директории для хранения треков если их не существует
        if not os.path.isdir(dir_original) and not os.path.isdir(dir_convert):
            os.makedirs(dir_original)
            os.makedirs(dir_convert)

        dir_result :dict= {
            'dir_original': dir_original,
            'dir_convert': dir_convert
                     }
        return dir_result


    def create_user_dir(self, name :str = '') -> dict:
        """Создает персональные пользвательские директории для хранения оригинальных и конвертируемых треков."""
        # В директориях для хранения треков добавляется директория пользователя с его именем-логином, id или иным
        # уникальным индификатором

        # Cоздается путь с пользовательской директорией в директории хранения треков
        if name != '':
            # user_dir_original = self.storage_dirs['dir_original'] + '/' + name
            # user_dir_convert = self.storage_dirs['dir_convert'] + '/' + name
            user_dir_original = os.path.normpath(os.path.join(self.storage_dirs['dir_original'], name))
            user_dir_convert = os.path.normpath(os.path.join(self.storage_dirs['dir_convert'], name))


            # Создаются пользовательские директории если их не существует
            if not os.path.isdir(user_dir_original) and not os.path.isdir(user_dir_convert):
                    os.makedirs(user_dir_original)
                    os.makedirs(user_dir_convert)

        # Если имя (логин, id) не указано, создаются пути общих директорий для хранения треков
        else:
            user_dir_original = self.storage_dirs['dir_original']
            user_dir_convert = self.storage_dirs['dir_convert']

        # Возвращение словаря с путями директорий для хранения треков
        result = {'name': name, 'user_dir_orig': user_dir_original, 'user_dir_convert': user_dir_convert}
        return result


    def convert(self, pathsound :str, frmt :str, name :str = '', )->dict :
        """Конвертирует аудио файл в указанный формат."""

        if frmt.lower() not in AudioConverter.formats:
            raise Exception("AudioConverter.convert 'Unknown format'")

        # Пути хранения треков
        user_dirs :dict = self.create_user_dir(name=name)
        trek_name: str = pathsound[pathsound.rfind("/") + 1:pathsound.rfind(".")].replace(" ", "_")
        trek_frmt: str = frmt.lower()

        trek  = AudioSegment.from_file(pathsound)
        export_path = f"{os.path.join(user_dirs['user_dir_convert'], trek_name)}.{trek_frmt}"
        # trek.export(f"{user_dirs['user_dir_convert']}/{trek_name}.{trek_frmt}", format=trek_frmt)
        trek.export(export_path, format=trek_frmt)

        # Флаг move определяет перемещение либо копирование исходного файла в директорию оригиналов
        if self.move == True:
            # Переместить трек в директорию оригиналов,если он там существует- перезаписать
            try:
                # trek_orig = shutil.move(pathsound, user_dirs['user_dir_orig']).replace('\\', "/")
                trek_orig = shutil.move(pathsound, user_dirs['user_dir_orig'])

            except shutil.Error:
                os.remove(user_dirs['user_dir_orig'] + pathsound[pathsound.rfind("/"):])
                # trek_orig = shutil.move(pathsound, user_dirs['user_dir_orig']).replace('\\', "/")
                trek_orig = shutil.move(pathsound, user_dirs['user_dir_orig'])

        # Копировать если флаг False
        else:
            trek_orig = shutil.copy(pathsound, user_dirs['user_dir_orig'])

        date: datetime = datetime.now()

        result :dict = {
            'user_name': name, # Имя пользователя
            'trek_name': trek_name, # Название трека
            'original_format': trek_orig[trek_orig.rfind(".")+1 :], # Формат исходного файла
            'path_original': trek_orig, # Путь к оригинальному файлу
            'path_convert': export_path, # Путь к конвертированному файлу
            'format': trek_frmt, # Формат конвертированного файла
            'date': date,  # Дата и время конвертирования
            'move': self.move # Флаг перемещения исходного файла в директорию оригиналов
                 }

        # Запись в бд информации о конвертированном файле
        if self.wirte_db == True:
            self.db.insert_audio(result)
        # breakpoint()
        return result



    def extract_audio(self, pathvideo :str, frmt :str = 'mp3', name :str = '', ):
        """Извлекает аудио из видео файла."""

        if frmt.lower() not in AudioConverter.formats:
            raise Exception("AudioConverter.convert 'Unknown format'")

        # Пути хранения треков
        user_dirs :dict = self.create_user_dir(name=name)
        video_name: str = pathvideo[pathvideo.rfind("/") + 1:pathvideo.rfind(".")].replace(" ", "_")
        trek_frmt: str = frmt.lower()
        output_v = f"{os.path.join(user_dirs['user_dir_convert'], video_name)}.{frmt}"

        subprocess.call(["ffmpeg", "-y", "-i", pathvideo, output_v],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)

        if self.move == True:
            # Переместить трек в директорию оригиналов,если он там существует- перезаписать
            try:
                trek_orig = shutil.move(pathvideo, user_dirs['user_dir_orig'])
            except shutil.Error:
                os.remove(user_dirs['user_dir_orig'] + pathvideo[pathvideo.rfind("/"):])
                trek_orig = shutil.move(pathvideo, user_dirs['user_dir_orig'])
        # Копировать если флаг False
        else:
            trek_orig = shutil.copy(pathvideo, user_dirs['user_dir_orig'])

        date: datetime = datetime.now()

        result :dict = {
            'user_name': name, # Имя пользователя
            'trek_name': video_name, # Название видео
            'original_format': trek_orig[trek_orig.rfind(".")+1 :], # Формат исходного файла
            'path_original': trek_orig, # Путь к оригинальному файлу
            'path_convert': output_v, # Путь к конвертированному файлу
            'format': trek_frmt, # Формат конвертированного файла
            'date': date,  # Дата и время конвертирования
            'move': self.move # Флаг перемещения исходного файла в директорию оригиналов
                 }

        # Запись в бд информации о конвертированном файле
        if self.wirte_db == True:
            self.db.insert_audio(result)

        return result


    @classmethod
    def available_formats(self) -> list:
        """Возвращает список доступных форматов для конвертирования."""
        return AudioConverter.formats


    @classmethod
    def show_objects(cls):
        result = {
            'AudioConverter': AudioConverter.number_converters,
            'AudioDataBase': AudioConverter.number_db
                }

        return result