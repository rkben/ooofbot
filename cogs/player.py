import re

import discord
import yt_dlp

from discord.ext import commands
from loguru import logger

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Tune:
    yid: str
    url: str
    title: str
    # TODO length; proper type (date) or that weird shit (str) youtube uses


class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_audio = None
        self.playlist: List[Optional[Tune]] = []

    def is_url(self, url: str):
        # TODO regex ^http(s):\/\/(.+)$ or something
        pass

    async def is_yt(self, url: str):
        # TODO regex  youtu(be\.com|\.be)
        pass

    async def search(self, query: str) -> str:
        """Search youtube with yt_dlp, ret url"""
        pass

    def best_format(self, data: dict) -> tuple:
        # actually just the biggest file, prefer opus cause its native iirc
        # (citation needed)
        best = (data[0]["filesize"], data[0]["url"])
        for entry in data["formats"][1:]:
            # TODO handle non-opus :(
            if entry["acodec"] == "opus" and entry["filesize"] > best[0]:
                best = (entry["filesize"], entry["url"])
        logger.debug(f"Using {best[0]}; {best[1]}")
        return best

    @commands.command(name="play", description="Play a tune")
    async def play(self, ctx: commands.Context):
        if ctx.author.voice is None:
            await ctx.send("You don't appear to be in a voice channel!")
        else:
            try:
                await ctx.author.voice.channel.connect()
            except:
                # TODO actual exception
                pass
            downloader = yt_dlp.YoutubeDL({"format": "bestaudio", "title": True})
            msg = ctx.message.content.lstrip(
                ";join "
            )  # TODO discord.py has thing for this
            # if self.is_url(msg.strip()):
            #   ret = downloader.extract_info(url, download=False)
            # else:
            #   search = await self.search(msg)
            #   something.something handle `ret`
            if msg.startswith("http"):
                url = msg.strip()
                ret = downloader.extract_info(url, download=False)
                logger.debug(ret)
            else:
                url = "ytsearch:" + msg.strip()
                ret = downloader.extract_info(url, download=False)["entries"]
                logger.debug(ret)
            title, url = self.best_format(ret)  # TODO dataclass cause im modern
            yid = ret["id"]
            # TODO dump to sqlite
            tune = Tune(yid, url, title)
            # TODO look at class opts
            self.active_audio = discord.FFmpegOpusAudio(
                url,
                before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            )
            # GROSS what the fuck
            try:
                ctx.author.guild.voice_client.play(self.active_audio)
                await ctx.send(f"Playing {title}")
            except:
                ctx.author.guild.voice_client.stop()
                ctx.author.guild.voice_client.play(self.active_audio)
                await ctx.send(f"Playing {title}")


def setup(bot):
    bot.add_cog(Player(bot))
