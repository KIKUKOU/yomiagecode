#!/usr/bin/env python3
"""
discord botのmainファイル.
bot起動時はこのmain.pyを実行する.
"""

import asyncio
import os

import discord
from discord.ext import commands

import utilities.config_utilities as confutl
import utilities.sound_utilities as sndutl
import utilities.text_utilities as txtutl
import yomiagecode.discord_functions as discordfunc
import yomiagecode.tts_functions as ttsfunc

# other
WEATHER_API_KEY = os.getenv('OPEN_WEATHER_MAP_API_KEY')
GCP_API_KEY = os.getenv('GOOGLE_CUSTOM_SEARCH_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CUSTOM_SEARCH_CSE_ID')

if __name__ == '__main__':
    # configファイルを読み込む
    configs = confutl.load_config('../data/config.yaml')

    # Discord bot permission settings
    intents = discord.Intents.default()
    intents.message_content = True  # permission to retrieve message content
    intents.voice_states = True
    discord_client = commands.Bot(command_prefix=configs['DISCORD']['COMMAND_PREFIX'], intents=intents)

    # TTS settings
    tts_client = ttsfunc.get_tts_client()

    @discord_client.command()
    async def join(
        ctx: commands.Context,
    ) -> None:
        """
        Join the voice channel of the user who invoked the command.

        Args:
            ctx (commands.Context): The context of the command invocation.
        """
        is_target_text_channel = ctx.channel.name == configs['DISCORD']['TARGET_TEXT_CHANNEL']
        is_user_in_voice_channel = ctx.message.author.voice is not None
        if is_target_text_channel:
            if is_user_in_voice_channel:
                await ctx.message.author.voice.channel.connect()
                send_text = 'ボイスチャンネルに接続しました'
                await discordfunc.send_message(ctx.message.channel, send_text)
            else:
                send_text = 'あなたがボイスチャンネルに入ってからコマンドを入力してください'
                await discordfunc.send_message(ctx.message.channel, send_text)

    @discord_client.command()
    async def bye(
        ctx: commands.Context,
    ) -> None:
        """
        Disconnect the bot from the voice channel.

        Args:
            ctx (commands.Context): The context of the command invocation.
        """
        is_target_text_channel = ctx.channel.name == configs['DISCORD']['TARGET_TEXT_CHANNEL']
        is_bot_in_voice_channel = ctx.message.guild.voice_client is not None
        if is_target_text_channel:
            if is_bot_in_voice_channel:
                await ctx.message.guild.voice_client.disconnect()
                send_text = 'さようなら'
                await discordfunc.send_message(ctx.message.channel, send_text)
            else:
                send_text = 'ボイスチャンネルには入っていません'
                await discordfunc.send_message(ctx.message.channel, send_text)

    @discord_client.event
    async def on_voice_state_update(
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        """
        Event handler for when user join a voice channel.
        """
        # ボットの動作は無視
        if member.bot:
            return

        # ユーザがVCに参加した場合
        is_channel_matched = after.channel.id == configs['DISCORD']['TARGET_VOICE_CHANNEL']
        if before.channel is None and after.channel is not None and is_channel_matched:
            if not after.channel.guild.voice_client:
                await after.channel.connect()

            sound_controller = sndutl.SoundController()
            user_name = member.display_name
            content = user_name + 'さんが参加しました'
            sound_file_name = ttsfunc.make_sound_file(content, tts_client, configs['TTS'])
            sound_controller = discordfunc.play_voice(after.channel.guild, sound_controller, sound_file_name)
            while not sound_controller.is_finish_all_thread():
                await asyncio.sleep(0.1)
                sound_controller.thread_control()

        # ユーザVCから離脱した場合
        elif before.channel is not None and after.channel is None:
            sound_controller = sndutl.SoundController()
            user_name = member.display_name
            content = user_name + 'さんが退出しました'
            sound_file_name = ttsfunc.make_sound_file(content, tts_client, configs['TTS'])
            sound_controller = discordfunc.play_voice(after.channel.guild, sound_controller, sound_file_name)
            while not sound_controller.is_finish_all_thread():
                await asyncio.sleep(0.1)
                sound_controller.thread_control()

            # ユーザが全員VCから離脱した場合
            if len(before.channel.members) == 1 and before.channel.guild.voice_client:
                await before.channel.guild.voice_client.disconnect()

    @discord_client.event
    async def on_message(
        message: discord.Message,
    ) -> None:
        """
        Event handler for incoming messages. Processes commands and generates AI responses.

        Args:
            message (discord.Message): The received message object.
        """
        is_human = not message.author.bot
        is_target_text_channel = message.channel.name == configs['DISCORD']['TARGET_TEXT_CHANNEL']
        is_voice_in = message.guild.voice_client is not None
        if len(message.content) > 0:
            is_command = message.content[0] == configs['DISCORD']['COMMAND_PREFIX']
        else:
            return

        if is_human and is_target_text_channel and not is_command and is_voice_in:
            sound_controller = sndutl.SoundController()
            user_name = message.author.display_name
            sound_file_name = ttsfunc.make_sound_file(user_name, tts_client, configs['TTS'])
            sound_controller = discordfunc.play_voice(message.guild, sound_controller, sound_file_name)

            word_marks = txtutl.WordMarks()
            text_buffer = ''
            is_make_voice = False
            message_text = message.content
            for letter in message_text:
                is_sp, is_p, is_e, is_q, is_n = word_marks.check_letter(letter)
                if not is_sp and is_make_voice and len(text_buffer) > 0:
                    text_buffer = txtutl.url2alternative_text(text_buffer, configs['TTS']['ALTERNATIVE_TEXT'])
                    sound_file_name = ttsfunc.make_sound_file(text_buffer, tts_client, configs['TTS'])
                    sound_controller = discordfunc.play_voice(message.guild, sound_controller, sound_file_name)

                    text_buffer = ''
                    await asyncio.sleep(0.1)

                if not is_n:
                    text_buffer = text_buffer + letter

                if is_sp:
                    is_make_voice = True

            text_buffer = txtutl.url2alternative_text(text_buffer, configs['TTS']['ALTERNATIVE_TEXT'])
            sound_file_name = ttsfunc.make_sound_file(text_buffer, tts_client, configs['TTS'])
            sound_controller = discordfunc.play_voice(message.guild, sound_controller, sound_file_name)
            while not sound_controller.is_finish_all_thread():
                await asyncio.sleep(0.1)
                sound_controller.thread_control()

            return

    discord_client.run(configs['DISCORD']['API_KEY'])
