# Commands & cogs for VSCode instances
from discord.ext import commands
from discord.ext.commands import Cog

import json
import aiohttp

class Dns(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dns(self, ctx, queryName: str, queryType: str = "A"):
        """Find a DNS record (uses 1.1.1.1 DoH)"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://"
                                   f"{self.bot.config['dns']['doh']['server']}"
                                   f"/dns-query?name={queryName}"
                                   f"&type={queryType}",
                                   headers={
                                       "accept": "application/dns-json"
                                   }) as resp:

                if resp.status == 200:
                    # Since the type is dns-json, resp.json() doesn't work
                    # So we need to do that manually
                    respJson = json.loads(await resp.text())
                    await ctx.send(f"```json\n{json.dumps(respJson, indent=4)}```")
                else:
                    await ctx.send(f"Failed to run query, HTTP Code: {resp.status}")

def setup(bot):
    bot.add_cog(Dns(bot))
