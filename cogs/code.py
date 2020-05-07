# Commands & cogs for VSCode instances
from discord.ext import commands
from discord.ext.commands import Cog

import helpers.docker


class Code(Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Code(bot))
