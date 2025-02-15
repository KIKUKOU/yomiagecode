#!/usr/bin/env python3
"""
discord bot用のクラス及び関数を定義したファイル.
"""

import time
from typing import Any

import discord
import ffmpeg

import utilities.sound_utilities as sndutl


async def send_message(channel: discord.TextChannel, send_text: str) -> None:
    """
    Send a message to a specified Discord channel.

    Args:
        channel (discord.TextChannel): The channel to send the message to.
        send_text (str): The text content of the message to send.
    """
    await channel.send(send_text)


async def reply_massage(message: discord.Message, reply_text: str) -> None:
    """
    Reply to a message with the given text.

    Args:
        message (discord.Message): The original message to reply to.
        reply_text (str): The text content of the reply.
    """
    reply = f'{message.author.mention} {reply_text}'
    await message.channel.send(reply)


def play_sound(guild: discord.Guild, file_name: str, configs: dict[str, Any]) -> None:
    """
    Play a sound file through the Discord voice client.

    Args:
        guild (discord.Guild): The received guild object.
        file_name (str): The path to the sound file to play.
        configs(dict[str, Any]): config辞書
    """
    voice_client = guild.voice_client
    video_info = ffmpeg.probe(file_name)
    dur = float(video_info['format']['duration'])
    fade_len = configs['FFMPEG']['FADE_LEN']
    opt = f'"afade=t=in:st=0:d={fade_len},afade=t=out:st={dur - fade_len}:d={fade_len}"'
    ffmpeg_options = {
        'options': f'-vn -af {opt}',
    }
    voice = discord.FFmpegPCMAudio(file_name, **ffmpeg_options)

    voice_client.play(voice)
    while voice_client.is_playing():
        time.sleep(0.1)

    voice_client.stop()


def play_voice(
    guild: discord.Guild,
    sound_controller: sndutl.SoundController,
    sound_file_name: str,
) -> sndutl.SoundController:
    # NOTE: どのTTSクライアントを受け取るかでどのクラスかが変わるのでAny.
    """
    Generate and play voice for the given text buffer.

    Args:
        guild (discord.Guild): The received Guild object.
        sound_controller (sound_util.SoundController): The sound controller object.
        sound_file_name (str): 音声ファイル名

    Returns:
        sound_util.SoundController: The updated sound controller.
    """
    # play voice
    # NOTE: Play audio while generating text with GPT and generating voice with VOICEVOX.
    #       For that purpose, we implemented parallel processing using threading.
    sound_controller.append_thread(
        play_sound,
        (guild, sound_file_name),
    )

    sound_controller.thread_control()
    return sound_controller
