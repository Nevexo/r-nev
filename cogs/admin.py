# Admin specific commands & checks

import discord
from discord.ext.commands import Cog
from discord.ext import commands


class Admin(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command()
    async def echo(self, ctx, *, txt: str):
        """Echo's out the string passed."""
        await ctx.send(f"`{txt}`")

    @commands.is_owner()
    @commands.command(aliases=["r"])
    async def reload(self, ctx, *, cog: str):
        """Reload the specified cog."""
        try:
            self.bot.unload_extension(f"cogs.{cog}")
            self.bot.load_extension(f"cogs.{cog}")
        except:
            await ctx.send(f"Failed to reload, see console.")
            return

        await ctx.send(f"{cog} reloaded.")

    @commands.is_owner()
    @commands.command()
    async def rc(self, ctx):
        """Reload the YAML config. (Ignores token)."""
        try:
            self.bot.config = self.bot.config_load()
        except:
            await ctx.send(":x: Failed to reload configuration, check console for traceback.")
            return

        await ctx.send(":white_check_mark: Config reloaded. Note that token updates "
                       "will not be applied until next restart.")

    @commands.is_owner()
    @commands.command()
    async def config(self, ctx):
        """Get the currently running configuration."""
        # Remove tokens

        cfg = str(self.bot.config)
        cfg = cfg.replace(self.bot.config['discord']['token'], "[DISCORD TOKEN]")

        await ctx.send(f"Running config: ```{cfg}```")


def setup(bot):
    bot.add_cog(Admin(bot))
