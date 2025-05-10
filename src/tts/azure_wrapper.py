#!/usr/bin/env python3
"""
The abstract class for wrap tts.
"""

import tempfile
from typing import Any

from azure.cognitiveservices.speech import AudioConfig, SpeechConfig, SpeechSynthesizer

from .tts_wrapper import TTSWrapper

# NOTE: https://learn.microsoft.com/ja-jp/azure/ai-services/speech-service/language-support?tabs=tts#text-to-speech .
#       分かりにくいのでAzureの設定についての参考リンク.


class AzureWrapper(TTSWrapper):
    """
    AzureのTTSを利用するためのWrapper.
    """

    def __init__(self, tts_configs: dict[str, Any] | None = None) -> None:
        """
        Initialize the TTS wrapper.

        Args:
            api_key (str): AzureのAPI key.
            region (str): AzureのAPI. 東日本; japaneast, 西日本; japanwest
            tts_configs (dict[str, Any] | None, optional): Configuration options for the TTS. Defaults to None.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        api_key = tts_configs['AZURE']['API_KEY']
        region = tts_configs['AZURE']['REGION']  # NOTE: AzureのAPI. 東日本; japaneast, 西日本; japanwest
        self.speech_config = SpeechConfig(
            subscription=api_key,
            region=region,
            speech_recognition_language='ja-JP',
        )
        if tts_configs['AZURE']['SPEAKER_ID'] != '':
            self.speech_config.speech_synthesis_voice_name = tts_configs['AZURE']['SPEAKER_ID']

        self.audio_config = AudioConfig(filename='')
        self.client = SpeechSynthesizer(speech_config=self.speech_config, audio_config=self.audio_config)
        self.speakers_name_dict = {
            'ja-JP-NanamiNeural': 'Nanami@Normal',
            'ja-JP-KeitaNeural': 'Keita@Normal',
            'ja-JP-AoiNeural': 'Aoi@Normal',
            'ja-JP-DaichiNeural': 'Daichi@Normal',
            'ja-JP-MayuNeural': 'Mayu@Normal',
            'ja-JP-NaokiNeural': 'Naoki@Normal',
            'ja-JP-ShioriNeural': 'Shiori@Normal',
            'ja-JP-MasaruMultilingualNeural': 'Masaru@Multilingual',
            'ja-JP-Masaru:DragonHDLatestNeural': 'Masaru@DragonHDLatest',
        }

    def generate_audio_query(self, text: str, tts_configs: dict[str, Any] | None = None) -> None:  # noqa: ARG002
        # NOTE: 他のAPIと合わせるためにデータは受けるが使わない.
        """
        Generate an audio query from the given text.

        Args:
            text (str): 音声変換したい文章
            tts_configs (dict[str, Any] | None): 他のAPIと合わせるために一旦受けるが捨てる

        Returns:
            str: クエリはstrの文章とみなして文章をそのまま返す
        """
        return text

    def generate_voice(
        self,
        audio_query: str,
        tts_configs: dict[str, Any] | None = None,
    ) -> bytes:
        """
        Generate voice data from the given audio query.

        Args:
            audio_query (None): 他のAPIと合わせるために一旦受けるが捨てる
            tts_configs (dict[str, Any]): Configuration options for voice generation. Defaults to None.

        Returns:
            Any: The generated voice data.
        """
        if tts_configs['AZURE']['SPEAKER_ID'] != '':
            self.speech_config.speech_synthesis_voice_name = tts_configs['AZURE']['SPEAKER_ID']
            self.client = SpeechSynthesizer(speech_config=self.speech_config, audio_config=self.audio_config)

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wf:
            wf.write(b'')
            file_path = wf.name

        self.audio_config = AudioConfig(filename=file_path)
        self.client = SpeechSynthesizer(speech_config=self.speech_config, audio_config=self.audio_config)
        self.client.speak_text_async(audio_query).get()
        return file_path
