#!/usr/bin/env python3
"""
The class wrap google tts.
"""

from __future__ import annotations

import copy
import math
from typing import TYPE_CHECKING, Any

from google.api_core.exceptions import GoogleAPICallError  # pip install google-cloud-texttospeech
from google.cloud import texttospeech  # pip install google-cloud-texttospeech

if TYPE_CHECKING:
    from google.cloud.texttospeech import SynthesisInput  # pip install google-cloud-texttospeech

from .tts_wrapper import TTSWrapper


class GoogleTTSWrapper(TTSWrapper):
    """
    Wrapper class for the Google-TTS API.

    This class provides methods to interact with the Google-TTS API.
    """

    def __init__(self, credential_file_name: str | None = None, config: dict[str, Any] | None = None) -> None:
        """
        Initialize the Google-TTS wrapper.

        Args:
            credential_file_name (str | None): The Google credential json file name.
                (ex. './hoge/fuga/credential.json') If it is None, use environment value.
                Default to None.
            config (dict[str, Any] | None, optional): Configuration options for the TTS.
                Defaults to None.
        """
        config = config or {}
        config = copy.deepcopy(config)

        if credential_file_name is None:
            self.client = texttospeech.TextToSpeechClient()
        else:
            self.client = texttospeech.TextToSpeechClient.from_service_account_json(credential_file_name)

        self.speakers_name_dict = {
            -1: 'NoVoice',
            1: 'ja-JP-Neural2-B',
            2: 'ja-JP-Neural2-C',
            3: 'ja-JP-Neural2-D',
        }

    def generate_audio_query(self, text: str, config: dict[str, Any] | None = None) -> SynthesisInput:
        """
        Generate an audio query from the given text.

        Args:
            text (str): The text to be converted to speech.
            config (dict[str, Any] | None, optional): Configuration options for the audio query.
                Defaults to None.

        Returns:
            SynthesisInput: The generated audio query for google-tts.
        """
        config = config or {}
        config = copy.deepcopy(config)

        return texttospeech.SynthesisInput(text=text)

    def generate_voice(self, audio_query: SynthesisInput, config: dict[str, Any] | None = None) -> bytes:
        """
        Generate voice data from the given audio query.

        Args:
            audio_query (SynthesisInput): The audio query to be converted to voice.
            config (dict[str, Any] | None, optional): Configuration options for voice generation.

        Returns:
            bytes: The generated voice data in wav format.

        Raises:
            RuntimeError: If there's an error in the API call.
        """
        config = config or {}
        config = copy.deepcopy(config)

        speaker_name = self.speakers_name_dict.get(config.get('speaker', 1))
        speaking_rate = config.get('speed', 1.25)
        volume_gain_db = self._calculate_volume_gain(config.get('volume', 1.0))
        language_code = config.get('language_code', 'ja-JP')

        voice = texttospeech.VoiceSelectionParams(
            name=speaker_name,
            language_code=language_code,
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=speaking_rate,
            volume_gain_db=volume_gain_db,
        )

        try:
            voice_data = self.client.synthesize_speech(input=audio_query, voice=voice, audio_config=audio_config)
        except GoogleAPICallError as e:
            raise_message = f'Failed to generate voice: {e!s}'
            raise RuntimeError(raise_message) from e
        else:
            return voice_data.audio_content

    @staticmethod
    def _calculate_volume_gain(volume: float) -> float:
        """
        Calculate volume gain in dB.

        Args:
            volume (float): Volume scale value.

        Returns:
            float: volume gain in dB.
        """
        return 20 * math.log10(volume)
