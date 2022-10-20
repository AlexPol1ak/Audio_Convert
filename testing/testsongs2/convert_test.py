import os
import asyncio
import time


from audiohandler.audio import AudioConverter
from audiohandler.asyncaudio import AsyncAudioConverter

# Converter settings
settings = {
        'move': False,
        'write_db': True,
        'db_path': 'tracks/data',
        'storage_path': 'tracks/sounds'
        }


# converter = AudioConverter(settings)  # synchronous converter
asnc_converter = AsyncAudioConverter(settings) # asynchronous converter

#file list
files = os.listdir()

audiofiles = []
for i in files:
    if i.endswith('.mp3'): # We'll remove only mp3 from all the files.
        audiofiles.append(i)

print(f'Numbers of audio {len(audiofiles)}',audiofiles) # <--- 24 audio
########################################################################################################################
                                                # synchronous converter

# start_time = time.time()
#
# for audio in audiofiles:
#     print(f'Convert {audio}')
#     converter.convert(pathsound=audio, frmt='wav', name='admin')
#
# end_time = time.time() - start_time
#
# print('Synchronous converter.\n', f"The {len(audiofiles)} audio take seconds to complete:  ", end_time)
# # 24 audio, 49.436 seconds

########################################################################################################################
                                                # asynchronous converter

async def main():
    tasks = []
    for audio in audiofiles:
        task = asyncio.create_task(asnc_converter.aconvert(pathsound=audio, frmt='wav', name='aAdmin'))
        tasks.append(task)


    print('The tasks were created by')
    r = await asyncio.gather(*tasks)
    print('Conversion complete')
    return r


start_time = time.time()
res = asyncio.run(main())
end_time = time.time() - start_time

print('Asynchronous converter.\n', f"The {len(audiofiles)} audio take seconds to complete:  ", end_time)
# 24 audio, 2.719 seconds, Wow:)
print(res)


########################################################################################################################
                                    # Extract audio from video in synchronous mode

# start_time = time.time()
#
# for vid in audiofiles:
#     print("Иззвлечение", vid)
#     converter.extract_audio(pathvideo=vid,frmt='mp3', name='Admin')
#
# end_time = time.time() - start_time
#
# print(f"It takes seconds to extract {len(audiofiles)} audio from the video:  ", end_time)
# # 5 video, 20.514 seconds

########################################################################################################################
                                    # Extract audio from video in asynchronous mode
#
# async def main():
#     tasks = []
#     for vid in audiofiles:
#         print("Creating a task", vid)
#         task = asyncio.create_task(asnc_converter.aextract_audio(pathvideo=vid,frmt='mp3', name='Admin'))
#         tasks.append(task)
#
#     print('Tasks have been created')
#     res = await asyncio.gather(*tasks)
#     print('Extraction completed')
#     return res
#
#
# start_time = time.time()
# res = asyncio.run(main())
# end_time = time.time() - start_time
#
# print(f"It takes seconds to extract {len(audiofiles)} audio from the video:  ", end_time)
# # 5 video, 0.370 seconds


