import os
import subprocess


def chek_system_ffmpeg() ->bool:
    """Проверяет наличие кодека ffmpeg в проекте и в системной переменной path Windows."""

    codecfolder = 'ffmpeg/bin'
    # Значение системной переменной
    systempath  = os.path.expandvars("$PATH")

    if systempath.find(codecfolder.replace('/', '\\'))>0:
        return True
    else:
        return False


def check_project_ffmpeg(pathffmpeg :str) -> str:
    """Проверяет наличие кодека ffmpeg в проекте."""

    codecfolder = 'ffmpeg/bin/ffmpeg.exe'
    codec = 'ffmpeg.exe'
    print(os.path.abspath(pathffmpeg))
    if os.path.exists(pathffmpeg) and pathffmpeg.find(codecfolder)>0:
        return os.path.abspath(pathffmpeg.replace(codec, ''))
    else:
        raise FileNotFoundError("Не найден кодек ffmpeg в проекте.")


def create_backup_dir(path :str = "") ->str:
    """Создает папку для хранения резервной копии системной переменной Windows - path."""

    name = 'backup_system_path'
    if path != '' and isinstance(path, str) and os.path.exists(path):
        backup_folder :str= f'{path}/{name}'
        try:
            os.mkdir(backup_folder)
        except FileExistsError:
            pass
        return backup_folder

    else:
        try:
            os.mkdir(name)
        except FileExistsError:
            pass
        return name


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

    recovery_file :str = f"{directory}/Path.txt"
    with open(recovery_file, "w", encoding="utf-8") as f1:
        for i in pathlist:
            f1.write(i+"\n")
    return os.path.abspath(recovery_file)


def addpath(path_ffmpeg :str) ->str:
    """Добалвяет путь в системную переменную path Windows."""

    # cmd = f'SETX MY_PATH "{path_ffmpeg}";"%PATH%" /M'
    # os.system(cmd)
    systempath :str = os.path.expandvars("$PATH")
    systempath :str = systempath.replace("C:\Windows", '%SystemRoot%')

    # bytes, ecoding='cp866'
    result :bytes = subprocess.check_output(['SETX', 'Path', f'{path_ffmpeg};{systempath}', '/M'], shell=True)
    reslultstr :str = result.decode("cp866")
    return reslultstr + "Перезапустите систему."


# Позволяет использвать кодек с бибилотекой pudub.Audiosigment и из командной строки
def connect_ffmpeg(pathffmpeg :str, backup :bool = False, buckup_folder :str = '' ,forcebly :bool = False):
    """Записывает кодек ffmpeg в системную переменную path Windows.
    Создает резервную копию системной переменной path."""

    flag_codec :bool = chek_system_ffmpeg()
    # Принудительная перезапись кодека
    if forcebly:
        flag_codec = False

    if flag_codec == False:
        ffmpeg :str= check_project_ffmpeg(pathffmpeg)
        if backup:
            backupfolder :str = create_backup_dir(buckup_folder)
            backuppath :str = create_backup_systempath(backupfolder)

        result = addpath(ffmpeg)
        print(result)
        return True
    else:
        print("Кодек ffmpeg уже добавлен в системную переменную path.")
        return True

ffmepgpath = '../audiohandler/ffmpeg/bin/ffmpeg.exe'



# Через bat
# def addpath(path_ffmpeg):
#     file_name = "add_ffmpeg_system_path.bat"
#     command = f'SETX MY_PATH "%PATH%";"{path_ffmpeg}" /M'
#     with open(file_name, "w", encoding="utf-8") as f:
#         f.write('@echo\n')
#         f.write(command)
#   # os.system(file_name)
#     return file_name