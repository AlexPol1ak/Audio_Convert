import asyncio
import os
import shutil
from datetime import datetime
import subprocess

from audiohandler.audio import AudioConverter


class AsyncAudioConverter(AudioConverter):

    def __init__(self, setting_dict :dict = None):
        super().__init__(setting_dict)

    def __repr__(self):
        return "Asynchronous version of AudioConverter"

    async def aconvert(self, pathsound :str, frmt :str, name :str = '', )-> dict:
        """Асинхронное конвретирование аудиофайлов."""

        # print("async.Конвертируем трек: ", pathsound)
        await asyncio.sleep(1 / 10000)

        if frmt.lower() not in self.formats:
            raise Exception("AudioConverter.convert 'Unknown format'")

        # Пути хранения треков
        user_dirs :dict = self.create_user_dir(name=name)
        trek_name: str = pathsound[pathsound.rfind("/") + 1:pathsound.rfind(".")].replace(" ", "_")
        trek_frmt: str = frmt.lower()
        outpt: str = f"{user_dirs['user_dir_convert']}/{trek_name}.{trek_frmt}"

        # Конвертируем трек
        result_subprocess = subprocess.Popen(['ffmpeg', '-i', pathsound, outpt], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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

        result: dict = {
            'user_name': name,  # Имя пользователя
            'trek_name': trek_name,  # Название трека
            'original_format': trek_orig[trek_orig.rfind(".") + 1:],  # Формат исходного файла
            'path_original': trek_orig,  # Путь к оригинальному файлу
            'path_convert': f"{user_dirs['user_dir_convert']}/{trek_name}.{trek_frmt}",
            # Путь к конвертированному файлу
            'format': trek_frmt,  # Формат конвертированного файла
            'date': str(date),  # Дата и время конвертирования
            'move': self.move,  # Флаг перемещения исходного файла в директорию оригиналов
            'result_subprocess': result_subprocess  # Результат работы субпроцесса
        }

        # Запись в бд информации о конвертированном файле
        if self.wirte_db == True:
            self.db.insert_audio(result)

        # print("async.Окончено конвертирование: ", trek_name)
        return result

    async def task_aconvert(self, pathsound: str, frmt: str, name: str = '') -> asyncio.tasks:
        """Получение задачи для асинхронного конвертирования аудиофайлов."""

        task = asyncio.create_task(self.aconvert(pathsound=pathsound, frmt=frmt, name=name))
        return task
