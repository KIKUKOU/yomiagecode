#!/usr/bin/env python3
"""
discord bot用のTTSに関する関数を載せたファイル.
"""

from typing import Any

import utilities.sound_utilities as sndutl
from tts.voicevox_wrapper import VoicevoxWrapper


def get_tts_client(tts_configs: dict | None = None) -> Any:  # noqa: ANN401
    # NOTE: どのTTSクライアントを受け取るかでどのクラスが戻るかは変わるのでAnyで返す.
    """
    TTSクライアントのクラスを受け取る関数.

    Args:
        tts_configs (dict or None): TTS用のconfig辞書

    Returns:
        Any: TTSクライアントオブジェクト
    """
    if tts_configs is None:
        tts_configs = {
            'USE_TTS': 'voicevox',
            'HOST_IP': '192.168.0.1',
            'PORT': 50021,
        }

    if tts_configs['USE_TTS'] == 'voicevox':
        tts_address = f'{tts_configs["HOST_IP"]}:{tts_configs["PORT"]}'
        tts_client = VoicevoxWrapper(tts_address)

    return tts_client


async def make_sound_file(text: str, tts_client: Any, tts_configs: dict | None) -> str:  # noqa: ANN401
    # NOTE: どのTTSクライアントを受け取るかでどのクラスかが変わるのでAny.
    """
    Generate and play voice for the given text buffer.

    Args:
        text (str): TTSで音声に変換する文章
        tts_client (Any): TTSクライアントオブジェクト
        tts_configs (dict or None): TTS用のconfig辞書

    Returns:
        str: voiceデータのファイルネーム
    """
    audio_query = tts_client.generate_audio_query(text, tts_configs)
    voice_data = tts_client.generate_voice(audio_query, tts_configs)
    return sndutl.generate_temp_wav(voice_data)
