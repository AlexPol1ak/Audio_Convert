import asyncio
import os
import shutil
from datetime import datetime
import subprocess

from audiohandler.audio import AudioConverter
from audiohandler.database.aaudioDB import aAudioDB


class AsyncAudioConverter(AudioConverter):
    """Асинхронный аудио конвертер."""

    def __init__(self, setting_dict :dict = None):
        """Инициализация настроек конвертор."""

        super().__init__(setting_dict=setting_dict)
        self.install_settings(sett_dict=setting_dict)


    def __repr__(self):
        return "Asynchronous version of AudioConverter"


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
                    self.db = aAudioDB(db_path = db_path)
                    AudioConverter.number_db += 1

                else:
                    # Создание базы данных в директории по умолчанию.
                    self.db = aAudioDB()
                    AudioConverter.number_db += 1


    async def aconvert(self, pathsound :str, frmt :str, name :str = '', )-> dict:
        """Асинхронное конвретирование аудиофайлов. Native coroutine function ."""

        await asyncio.sleep(1 / 1000)

        if frmt.lower() not in AsyncAudioConverter.formats:
            raise Exception("AsyncAudioConverter.convert 'Unknown format'")

        # Пути хранения треков
        user_dirs :dict = self.create_user_dir(name=name)
        trek_name: str = pathsound[pathsound.rfind("/") + 1:pathsound.rfind(".")].replace(" ", "_")
        trek_frmt: str = frmt.lower()
        # outpt: str = f"{user_dirs['user_dir_convert']}/{trek_name}.{trek_frmt}"
        outpt:str = f"{os.path.join(user_dirs['user_dir_convert'], trek_name)}.{trek_frmt}"

        # Конвертируем трек

        result_subprocess = subprocess.Popen(['ffmpeg', '-i', pathsound, outpt], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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

        result: dict = {
            'user_name': name,  # Имя пользователя
            'trek_name': trek_name,  # Название трека
            'original_format': trek_orig[trek_orig.rfind(".") + 1:],  # Формат исходного файла
            'path_original': trek_orig,  # Путь к оригинальному файлу
            'path_convert': outpt,
            # Путь к конвертированному файлу
            'format': trek_frmt,  # Формат конвертированного файла
            'date': date,  # Дата и время конвертирования
            'move': self.move,  # Флаг перемещения исходного файла в директорию оригиналов
            'result_subprocess': result_subprocess  # Результат работы субпроцесса
        }

        # Запись в бд информации о конвертированном файле
        if self.wirte_db == True:
            await self.db.ainsert_audio(result)

        return result


    async def task_aconvert(self, pathsound: str, frmt: str, name: str = '') -> asyncio.tasks:
        """Получение задачи для асинхронного конвертирования аудиофайлов.
            Возвращает  объект asyncio.Task.
        """
        # Планирует ее выполнение в ближайшее время
        # Асинхронный запуск создаваемых задач можно планировать при помощи функции asyncio.gather().

        task = asyncio.create_task(self.aconvert(pathsound=pathsound, frmt=frmt, name=name))
        return task


    async def aextract_audio(self, pathvideo :str, frmt :str = 'mp3', name :str = '', ):
        """Асинхронное извлечение аудио из видео файла. Native coroutine function ."""

        await asyncio.sleep(1/10000)

        if frmt.lower() not in AsyncAudioConverter.formats:
            raise Exception("AudioConverter.convert 'Unknown format'")

        # Пути хранения треков
        user_dirs :dict = self.create_user_dir(name=name)
        video_name: str = pathvideo[pathvideo.rfind("/") + 1:pathvideo.rfind(".")].replace(" ", "_")
        trek_frmt: str = frmt.lower()

        output = f"{os.path.join(user_dirs['user_dir_convert'], video_name)}.{frmt}"

        subprocess.Popen(["ffmpeg", "-y", "-i", pathvideo, output],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)

        await asyncio.sleep(1 / 10000)

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
            'path_convert': output, # Путь к конвертированному файлу
            'format': trek_frmt, # Формат конвертированного файла
            'date': date,  # Дата и время конвертирования
            'move': self.move # Флаг перемещения исходного файла в директорию оригиналов
                 }

        # Запись в бд информации о конвертированном файле
        if self.wirte_db == True:
            await self.db.ainsert_audio(result)

        return result


    async def task_aextract_audio(self, pathvideo :str, frmt :str = 'mp3', name :str = '', ) -> asyncio.tasks:
        """Получение задачи для асинхронного извлечения аудио из видео.
            Возвращает объект asyncio.Task.
        """
        # Планирует ее выполнение в ближайшее время
        # Асинхронный запуск создаваемых задач можно планировать при помощи функции asyncio.gather().

        task = asyncio.create_task(self.aextract_audio(pathvideo=pathvideo, frmt=frmt, name=name))
        return task


    def aconvert_all(self, trackslist :list[str], frmt :str = 'mp3', name :str= ""):
        """"Асинхронное конвертирование последовательнсти музыкальных треков."""

        loop :asyncio = asyncio.get_event_loop()
        tasks :list = []
        if frmt.lower() not in AsyncAudioConverter.formats:
            loop.close()
            raise Exception("AsyncAudioConverter.convert 'Unknown format'")

        for i in trackslist:
            task = loop.create_task(self.aconvert(pathsound=i, frmt=frmt, name=name))
            tasks.append(task)

        # Список словарей с информацией о каждом конвертированном файле
        result = loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()

        return result
