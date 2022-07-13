from codecsetting import connect_ffmpeg
# Только относительный путь к кодеку ffmpeg
ffmpeg = './ffmpeg/bin/ffmpeg.exe'
connect_ffmpeg(pathffmpeg=ffmpeg, backup=False, forcebly=False)

from pydub import AudioSegment
import os
import shutil
from datetime import datetime



class AudioConverter():
    """Аудио конвертер."""

    formats: list[str] = ['ac3', 'asf', 'Flac', 'mp3', 'mp4', 'mov', "ogg", 'wav', ]  # '-AAC' '-DTS' '-wma'

    @classmethod
    def create_user_dir(cls, path :str = "",  name :str = '') -> dict:
        """Создает директории для хранения оригинальных и конвертируемых треков."""

        # Имена директорий
        dir_original = 'original_tracks'
        dir_convert = 'convertible_tracks'

        # Формирует путь создания директорий, если указано иное место хранения
        if path != '' and os.path.exists(path):
            dir_original = path + '/' + dir_original
            dir_convert = path + '/' + dir_convert
        # Формирует путь создания персональных директорий, если указано имя
        if name != '':
            dir_original = dir_original + '/' + name
            dir_convert = dir_convert + '/' + name

        # Создает директории если не существуют
        if not os.path.isdir(dir_original) and not os.path.isdir(dir_convert):
            if name != '':
                os.makedirs(dir_original)
                os.makedirs(dir_convert)
            else:
                os.mkdir(dir_original)
                os.mkdir(dir_convert)

        result = {'name': name, 'dir_original': dir_original, 'dir_convert': dir_convert}

        return result

    @classmethod
    def convert(cls, pathsound :str, format :str, name :str = '', savepath :str = '', move :bool = True)->dict :
        """Конвертирует аудио файл в указанный формат."""

        if format.lower() not in AudioConverter.formats:
            raise Exception("AudioConverter.convert 'Unknown format'")

        user_dirs :dict = AudioConverter.create_user_dir(path=savepath,name=name)
        trek_name: str = pathsound[pathsound.rfind("/") + 1:pathsound.rfind(".")].replace(" ", "_")
        trek_frmt: str = format.lower()

        trek = AudioSegment.from_file(pathsound)
        trek.export(f"{user_dirs['dir_convert']}/{trek_name}.{trek_frmt}", format=trek_frmt)

        # Флаг move определяет перемещение либо копирование исходного файла в директорию оригиналов
        if move == True:
            try:
                trek_orig = shutil.move(pathsound, user_dirs['dir_original']).replace('\\', "/")
            except shutil.Error:
                os.remove(user_dirs['dir_original'] + pathsound[pathsound.rfind("/"):])
                trek_orig = shutil.move(pathsound, user_dirs['dir_original']).replace('\\', "/")
        else:
            trek_orig = shutil.copy(pathsound, user_dirs['dir_original']).replace('\\', "/")

        date: datetime = datetime.now()

        result = {
            'user_name': name, # Имя пользователя
            'trek_name': trek_name, # Название трека
            'original_format': trek_orig[trek_orig.rfind(".")+1 :], # Формат исходного файла
            'path_original': trek_orig, # Путь к оригинальному файлу
            'path_convert': f"{user_dirs['dir_convert']}/{trek_name}.{trek_frmt}", # Путь к конвертированному файлу
            'format': trek_frmt, # Формат конвертированного файла
            'date': str(date),  # Дата и время конвертирования
            'move': move # Флаг перемещения исходного файла в директорию оригиналов
                 }

        return result

    @classmethod
    def available_formats(cls) -> list:
        """Возвращает список доступных форматов для конвертирования."""
        return AudioConverter.formats

    @classmethod
    def write_db(cls, data :dict):
        pass









