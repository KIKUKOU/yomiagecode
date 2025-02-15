#!/usr/bin/env python3
"""
The class and functions for play wav sound.
"""

import logging
import tempfile
import threading
import wave

import pyaudio as audio  # pip install pyaudio

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SoundController:
    """
    The class and functions for play wav sound.
    """

    def __init__(self) -> None:
        """
        The class and functions for play wav sound.
        """
        self.thread_list = []
        self.thread_status_list = []

    def append_thread(self, func: str | None, args: tuple) -> None:
        """
        Apeend play wav sound thread.

        Args:
            func(Callable[[str], None]): Target function.
            args(tuple): Function arguments.
        """
        self.thread_list.append(threading.Thread(target=func, args=args))
        self.thread_status_list.append('before_start')

    def thread_control(self) -> None:
        """
        Start thread if lataset start thread is finished.
        """
        if self.thread_status_list == []:
            return

        for idx, status in enumerate(self.thread_status_list):
            if idx > 0 and self.thread_status_list[idx - 1] != 'finish':
                break

            if status == 'before_start':
                self.thread_list[idx].start()
                self.thread_status_list[idx] = 'running'
                break
            elif status == 'running':  # noqa: RET508
                # NOTE: Do not break.
                if not self.thread_list[idx].is_alive():
                    self.thread_status_list[idx] = 'finish'
                    break

        return

    def is_finish_all_thread(self) -> bool:
        """
        Check all thread finished.
        """
        is_fin = False
        if self.thread_status_list[-1] == 'finish':
            is_fin = True

        return is_fin


def generate_wav(data: bytes, file_name: str = './sound_files/audio.wav') -> str:
    """
    Generate wav file.

    Args:
        data(bytes): sound data.
        file_name(str, optional): wav file name.
    """
    with wave.open(file_name, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(data)

    return file_name


def generate_temp_wav(data: bytes) -> str:
    """
    Generate wav file at temporary file.

    Args:
        data(bytes): sound data.
    """
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wf:
        wf.write(data)
        return wf.name


def play_wav(file_name: str) -> None:
    """
    Play wav file.
    """
    chunk = 1024
    with wave.open(file_name, 'rb') as wav_obj:
        audio_obj = audio.PyAudio()
        stream = audio_obj.open(
            format=audio_obj.get_format_from_width(wav_obj.getsampwidth()),
            channels=wav_obj.getnchannels(),
            rate=wav_obj.getframerate(),
            output=True,
        )
        data = wav_obj.readframes(chunk)
        while len(data := wav_obj.readframes(chunk)):
            stream.write(data)

        stream.stop_stream()
        stream.close()
        audio_obj.terminate()
    return
