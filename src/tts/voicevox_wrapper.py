#!/usr/bin/env python3
"""
The class wrap google tts.
"""

from __future__ import annotations

import copy
import json
from typing import Any

import requests  # pip install requests
from requests.exceptions import RequestException  # pip install requests

from .tts_wrapper import TTSWrapper


class VoicevoxWrapper(TTSWrapper):
    """
    Wrapper class for the VOICEVOX API.

    This class provides methods to interact with the VOICEVOX API.
    """

    def __init__(
        self,
        address: str = '127.0.0.1:50021',
        tts_configs: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the voicevox wrapper.

        Args:
            address (str): The Voicevox server ip address with port. Dafault in '127.0.0.1:50021'.
            tts_configs (dict[str, Any], optional): Configuration options for the TTS. Defaults to None.
        """
        tts_configs = tts_configs or {}
        tts_configs = copy.deepcopy(tts_configs)

        self.client = f'http://{address}'
        self.speakers_name_dict = {-1: 'NoVoice'}
        self.speakers_name_dict = self.speakers_name_dict | self._fetch_speakers()

    def generate_audio_query(
        self,
        text: str,
        tts_configs: dict[str, Any] | None = None,
    ) -> dict:
        """
        Generate an audio query from the given text.

        Args:
            text (str): The text to be converted to speech.
            tts_configs (dict[str, Any]): Configuration options for the audio query.  Defaults to None.

        Returns:
            dict: The generated audio query for voicevox.

        Raises:
            RuntimeError: If there's an error in the API call.
        """
        tts_configs = copy.deepcopy(tts_configs)
        params = {
            'text': text,
            'speedScale': tts_configs['VOICEVOX'].get('SPEED_SCALE', 1.0),
            'volumeScale': tts_configs['VOICEVOX'].get('VOLUME_SCALE', 1.0),
            'speaker': tts_configs['VOICEVOX'].get('SPEAKER_ID', 1),
        }

        try:
            with requests.post(f'{self.client}/audio_query', params=params, timeout=5) as response:
                response.raise_for_status()
                audio_query = response.json()
        except RequestException as e:
            raise_massage = f'Failed to generate audio query: {e!s}'
            raise RuntimeError(raise_massage) from e
        else:
            return audio_query

    def generate_voice(
        self,
        audio_query: dict,
        tts_configs: dict[str, Any] | None = None,
    ) -> bytes:
        """
        Generate voice data from the given audio query.

        Args:
            audio_query (dict): The audio query to be converted to voice.
            tts_configs (dict[str, Any]): Configuration options for voice generation. Defaults to None.

        Returns:
            bytes: The generated voice data in wav format.

        Raises:
            RuntimeError: If there's an error in the API call.
        """
        tts_configs = copy.deepcopy(tts_configs)
        params = {
            'speaker': tts_configs['VOICEVOX'].get('SPEAKER_ID', 1),
        }
        headers = {
            'Content-Type': 'application/json',
        }

        try:
            with requests.post(
                f'{self.client}/synthesis',
                headers=headers,
                params=params,
                data=json.dumps(audio_query),
                timeout=30,
            ) as response:
                response.raise_for_status()
        except RequestException as e:
            raise_message = f'Failed to generate voice: {e!s}'
            raise RuntimeError(raise_message) from e
        else:
            return response.content

    def _fetch_speakers(self) -> dict[str, str]:
        """
        Initialize the voicevox wrapper.

        Returns:
            dict[str, str]: The dictionary of speakers, keyed by id.

        Raises:
            RuntimeError: If there's an error in the API call.
        """
        speakers_name_dict = {}
        try:
            with requests.get(f'{self.client}/speakers', timeout=5) as response:
                response.raise_for_status()
                response_dict = response.json()
                for i in response_dict:
                    for s in i['styles']:
                        speakers_name_dict[int(s['id'])] = f'{i["name"]}@{s["name"]}'

        except RequestException as e:
            raise_message = f'Failed to fetch speakers: {e!s}'
            raise RuntimeError(raise_message) from e
        else:
            return speakers_name_dict
