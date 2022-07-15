from .codecsetting  import connect_ffmpeg
connect_ffmpeg(pathffmpeg='./ffmpeg/bin/ffmpeg.exe', backup=False, forcebly=False)

from .database import audioDB

from pydub import AudioSegment
import os
import shutil
from datetime import datetime



class AudioConverter():
    """Аудио конвертер."""

    amount = 0

    def __init__(self, setting_dict :dict = None):
        """Инициализация настроек конвертора."""

        self.formats :list[str] = ['ac3', 'asf', 'Flac', 'mp3', 'mp4', 'mov', "ogg", 'wav', ]  # '-AAC' '-DTS' '-wma'

        self.storage_path :str = '' # путь к директории для хранения оригинальных и конвертируемых треков
        self.move :bool = False # перемещать оригинальные треки в директорию оригиналов
        self.write_db :bool = False # записывать данные в базу данных

        # Устнановка настроек со словаря.
        self.install_settings(setting_dict)
        # Создание директорий для хранения треков если их не существует
        self.storage_dirs :dict = self.create_storage_dirs() # пути к директориям для хранения треков
        # Количество объектов класса
        AudioConverter.amount += 1


    def install_settings(self, sett_dict :dict) ->None:
        """Установка настроек конвертора."""

        if isinstance(sett_dict, dict):
            path  = sett_dict.get('storage_path', '')
            if os.path.exists(path):
                self.storage_path = path

            move = sett_dict.get('move', False)
            if isinstance(move, bool):
                self.move = move

            write_db = sett_dict.get('write_db', False)
            if isinstance(write_db, bool):
                self.write_db= write_db


    def create_storage_dirs(self) -> dict :
        """Создает директории для хранения оригинальных и конвертируемых треков."""

        dir_original = 'original_tracks'
        dir_convert = 'convertible_tracks'

        # Если укзан путь- дериктории для хранения треков создаются по указанному пути
        if self.storage_path != '' and os.path.exists(self.storage_path):
            dir_original = self.storage_path + '/' + dir_original
            dir_convert = self.storage_path + '/' + dir_convert

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
            user_dir_original = self.storage_dirs['dir_original'] + '/' + name
            user_dir_convert = self.storage_dirs['dir_convert'] + '/' + name

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


    def convert(self, pathsound :str, format :str, name :str = '', )->dict :
        """Конвертирует аудио файл в указанный формат."""

        if format.lower() not in self.formats:
            raise Exception("AudioConverter.convert 'Unknown format'")

        # Пути хрванения треков
        user_dirs :dict = self.create_user_dir(name=name)
        trek_name: str = pathsound[pathsound.rfind("/") + 1:pathsound.rfind(".")].replace(" ", "_")
        trek_frmt: str = format.lower()

        trek  = AudioSegment.from_file(pathsound)
        trek.export(f"{user_dirs['user_dir_convert']}/{trek_name}.{trek_frmt}", format=trek_frmt)

        # Флаг move определяет перемещение либо копирование исходного файла в директорию оригиналов
        if self.move == True:
            # Переместить трек в директорию оригиналов,если он там существует- перезаписать
            try:
                trek_orig = shutil.move(pathsound, user_dirs['user_dir_orig']).replace('\\', "/")
            except shutil.Error:
                os.remove(user_dirs['user_dir_orig'] + pathsound[pathsound.rfind("/"):])
                trek_orig = shutil.move(pathsound, user_dirs['user_dir_orig']).replace('\\', "/")
        # Копировать если флаг False
        else:
            trek_orig = shutil.copy(pathsound, user_dirs['user_dir_orig']).replace('\\', "/")

        date: datetime = datetime.now()

        result :dict = {
            'user_name': name, # Имя пользователя
            'trek_name': trek_name, # Название трека
            'original_format': trek_orig[trek_orig.rfind(".")+1 :], # Формат исходного файла
            'path_original': trek_orig, # Путь к оригинальному файлу
            'path_convert': f"{user_dirs['user_dir_convert']}/{trek_name}.{trek_frmt}", # Путь к конвертированному файлу
            'format': trek_frmt, # Формат конвертированного файла
            'date': str(date),  # Дата и время конвертирования
            'move': self.move # Флаг перемещения исходного файла в директорию оригиналов
                 }


        return result


    def available_formats(self) -> list:
        """Возвращает список доступных форматов для конвертирования."""
        return self.formats


    def create_db(self, path):
        pass
    # Создать папку , в ней бд, если папка существует нечего не создовать


    def write_db(self, data :dict):
        pass
    # Записать данные в бд ,если бд есть

    @classmethod
    def number_objects(cls):
        return AudioConverter.amount







