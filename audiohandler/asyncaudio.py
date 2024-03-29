import asyncio
import os
import shutil
from datetime import datetime
import subprocess

from .audio import AudioConverter
from .database.aaudioDB import aAudioDB


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
        audio_name: str = os.path.splitext(os.path.split(pathsound)[1].replace(" ", "_"))[0]
        audio_frmt: str = frmt.lower()
        outpt:str = f"{os.path.join(user_dirs['user_dir_convert'], audio_name)}.{audio_frmt}"

        # Конвертируем трек
        result_subprocess = subprocess.Popen(['ffmpeg', '-i', pathsound, outpt], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        await asyncio.sleep(1 / 1000)
        # Флаг move определяет перемещение либо копирование исходного файла в директорию оригиналов
        if self.move == True:
            # Переместить трек в директорию оригиналов,если он там существует- перезаписать
            try:
                audio_orig = shutil.move(pathsound, user_dirs['user_dir_orig'])
            except shutil.Error:
                os.remove(os.path.join(user_dirs['user_dir_orig'],os.path.split(pathsound)[1]))
                audio_orig = shutil.move(pathsound, user_dirs['user_dir_orig'])
        # Копировать если флаг False
        else:
            audio_orig = shutil.copy(pathsound, user_dirs['user_dir_orig'])
        await asyncio.sleep(1 / 1000)


        # Запись данных об операции в словарь.
        result: dict = self.get_audio_info(user_name=name, audio_name=audio_name, path_original=audio_orig, frmt=audio_frmt,
                                           path_convert=outpt)
        result.update(result_subprocess=result_subprocess) #Резульатат работы субпроцесса

        # Запись в бд информации о конвертированном файле
        await asyncio.sleep(1 / 1000)
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
        video_frmt: str = frmt.lower()
        output = f"{os.path.join(user_dirs['user_dir_convert'], video_name)}.{frmt}"

        subprocess.Popen(["ffmpeg", "-y", "-i", pathvideo, output],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)

        await asyncio.sleep(1 / 10000)

        if self.move == True:
            # Переместить трек в директорию оригиналов,если он там существует- перезаписать
            try:
                audio_orig = shutil.move(pathvideo, user_dirs['user_dir_orig'])
            except shutil.Error:
                os.remove(user_dirs['user_dir_orig'] + pathvideo[pathvideo.rfind("/"):])
                audio_orig = shutil.move(pathvideo, user_dirs['user_dir_orig'])
        # Копировать если флаг False
        else:
            audio_orig = shutil.copy(pathvideo, user_dirs['user_dir_orig'])

        # Запись данных об операции в словарь.
        result: dict = self.get_audio_info(user_name=name, audio_name=video_name, path_original=audio_orig, frmt=video_frmt,
                                           path_convert=output)

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
