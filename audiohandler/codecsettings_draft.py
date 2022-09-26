import os
import subprocess

def check_project_ffmpeg(pathffmpeg :str = None) -> str:
    """Проверяет наличие кодека ffmpeg в проекте."""

    codecfolder = 'ffmpeg/bin/ffmpeg.exe'
    codec = 'ffmpeg.exe'

    # Если не указан путь к кодеку- проверят наличие кодека в текущем проекте
    if not pathffmpeg:
        if os.path.exists(codecfolder):
            return os.path.split(os.path.abspath(codecfolder))[0]
        else:
            raise FileNotFoundError (" Ffmpeg codeс not found in project")
    # Если указан путь - проверяет наличие кодека по указанному пути, и соответствие директорий согласно требованиям
    # библиотеки pydub
    elif pathffmpeg:
        if os.path.exists(pathffmpeg) and pathffmpeg.find(codecfolder)>0:
            return os.path.split(os.path.abspath(pathffmpeg))[0]
        else:
            raise FileNotFoundError (" Path specified incorrectly")

    else:
        raise FileNotFoundError("Ffmpeg codec not found")


def create_backup_dir() ->str:
    """Создает папку для хранения резервной копии системной переменной path."""

    name = 'backup_system_path'

    os.chdir('..')
    try:
        os.mkdir(name)
    except FileExistsError:
        pass
    path  = os.path.join(os.getcwd(), name)

    return path


def create_backup_systempath(directory :str) ->str:
    """Создает резеврную копию системной переменной path."""

    pathstr :str = os.path.expandvars("$PATH")
    pathlist_draft :list[str] = pathstr.split(";")
    pathlist :list[str]= []
    # Список путей из системной переменной path для резервной копии
    for i in pathlist_draft:
        if i.startswith("C:\Windows"):
            i = i.replace("C:\Windows", "%SystemRoot%")
        pathlist.append(i)
    pathlist.pop(-1)

    # Запись всех значений в файл txt.
    recovery_file :str = f"{directory}/Path.txt"
    with open(recovery_file, "w", encoding="utf-8") as f1:
        for i in pathlist:
            f1.write(i+"\n")
    return os.path.abspath(recovery_file)


def create_recovery_bat(backup_dir :str ,backup_sys_path :str) ->None:
    """Создает bat файл востановления."""

    # Создание bat файла  командой создания системной переменной Path
    file = f"{backup_dir}\\run_recovery.bat"
    with open(file, 'w', encoding='utf-8') as bat:

        with open(backup_sys_path, 'r', encoding='utf-8') as txt:

            paths_lst :list = txt.readlines()
            paths_str :str = ';'.join(paths_lst).replace('\n', '')
            command = f'SETX Path "{paths_str}" /M'
            bat.write(command)

    # Запись напоминания о запуске с правами администратора
    instruction = f"{backup_dir}\\read.txt"
    with open(instruction, 'w', encoding='utf-8') as instr:
        instr.write('Run the run_recovery.bat with administrator rights!!!')


def addpath(pathffmpeg :str) ->str:
    """Добалвяет путь в системную переменную path Windows."""

    # cmd = f'SETX MY_PATH "{path_ffmpeg}";"%PATH%" /M'
    # os.system(cmd)
    systempath :str = os.path.expandvars("$PATH")
    systempath :str = systempath.replace("C:\Windows", '%SystemRoot%')
    print( f'{pathffmpeg};{systempath}')

    # bytes, ecoding='cp866'
    result :bytes = subprocess.check_output(['SETX', 'Path', f'{pathffmpeg};{systempath}', '/M'], shell=True)
    try:
        reslultstr :str = result.decode("cp866")
    except:
        reslultstr = '$Успех. Указанное значение сохранено.'
    return reslultstr + "Перезапустите систему."


# Позволяет использвать кодек с бибилотекой pudub.Audiosigment и из командной строки
def connect_ffmpeg(pathffmpeg=None, backup=False) -> dict:
    """Проверяет наличие в системе кодека ffmpeg.Пытается подключить его при его отсуствии."""

    info = {}
    # Проверить есть ли в системе кодек ffmpeg.
    try:
        cmd = 'ffmpeg -version'
        result  = subprocess.check_output(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        info.update({'status': result})
    except subprocess.CalledProcessError:

        # Если в системе нет кодека - проверить есть ли он в проекте или по указанному пути
        # Если указан pathffmpeg -проверяет наличие кодека в нем, если  не указан pathffmpeg- проверяет в
        # директории audiohandler. Если кодек не найден - генерирует исключение
        result = check_project_ffmpeg(pathffmpeg=pathffmpeg)

        # Если backup = True - создать резервную копию системной переменной Path.
        if backup:
            # Создает директорию с резервными файлами
            backup_dir :str = create_backup_dir()
            # Создает txt файл со значениями сист прем. Path
            backup_sys_path :str = create_backup_systempath(directory=backup_dir)
            # Создает bat файл c командой и значениями переменной Path,
            # запуск которого создаст сист. перем. Path. Создает напоминание о запуске с админ. правамию
            create_recovery_bat(backup_dir=backup_dir, backup_sys_path=backup_sys_path)

            info.update({'backup': backup_sys_path})
        # Запись в сист. перем. Path путь к кодеку (путь к файлу ffmpeg.exe).
        try:
            state = addpath(pathffmpeg=result)
        except:
            raise Exception ("Error adding codec to system variable")
        else:
            info.update({'status': state})

    return info

