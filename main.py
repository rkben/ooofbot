"""
url: https://discord.com/api/oauth2/authorize?client_id=989621934276874330&permissions=36826176&scope=bot
"""
import time
import discord
from discord.ext import commands
from loguru import logger
from dataclasses import dataclass
from typing import List


@dataclass
class Configuration:
    prefix: str
    perms: int
    token: str
    cogs: List[str]


class Mbot(commands.Bot):
    def __init__(self, config: Configuration):
        self.config = config
        super().__init__(command_prefix=self.config.prefix)

    async def on_ready(self):
        await self.wait_until_ready()
        logger.info(list(self.get_all_members()))
        await self.load()

    async def load(self):
        for cog in self.config.cogs:
            try:
                self.load_extension("cogs." + cog)
            except commands.ExtensionNotFound as e:
                logger.error(f"Failed to load {cog}")
                logger.error(e)
            except commands.ExtensionFailed as e:
                logger.error(f"Failed to load {cog}")
                logger.error(e)
            except commands.NoEntryPointError as e:
                logger.error(e)
                logger.error(f"Failed to load {cog}")
            else:
                logger.info(f"Loaded {cog}")


perms = 36785216
token = "" # TODO config.conf.config.dataclass.config
c = Configuration(prefix=";", perms=perms, token=token, cogs=["player"])
b = Mbot(config=c)
b.run(c.token)
