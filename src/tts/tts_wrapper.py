#!/usr/bin/env python3
"""
The abstract class for wrap tts.
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any


class TTSWrapper(metaclass=ABCMeta):
    """
    Abstract base class for TTS (Text To Speech) API wrappers.

    This class defines the interface for interacting with various TTS APIs.
    """

    @abstractmethod
    def __init__(
        self,
        tts_configs: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the TTS wrapper.

        Args:
            tts_configs (dict[str, Any] | None, optional): Configuration options for the TTS. Defaults to None.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        self.client = []
        self.speakers_name_dict = {}
        raise_massage = 'Subclasses must implement __init__'
        raise NotImplementedError(raise_massage)

    @abstractmethod
    def generate_audio_query(self, text: str, tts_configs: dict[str, Any] | None = None) -> Any:
        """
        Generate an audio query from the given text.

        Args:
            text (str): The text to be converted to speech.
            tts_configs (dict[str, Any] | None): Configuration options for the audio query. Defaults to None.

        Returns:
            Any: The generated audio query.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        raise_message = 'Subclasses must implement generate_audio_query'
        raise NotImplementedError(raise_message)

    @abstractmethod
    def generate_voice(
        self,
        audio_query: Any,
        tts_configs: dict[str, Any] | None = None,
    ) -> bytes:
        """
        Generate voice data from the given audio query.

        Args:
            audio_query (Any): The audio query to be converted to voice.
            tts_configs (dict[str, Any]): Configuration options for voice generation. Defaults to None.

        Returns:
            Any: The generated voice data.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        raise_message = 'Subclasses must implement generate_voice'
        raise NotImplementedError(raise_message)
