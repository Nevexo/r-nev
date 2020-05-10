# r.nev 3.0, a utility bot.
import asyncio

import discord
import traceback
import yaml
from discord.ext import commands
import logging, logging.handlers
import re

config = {}
code_regex = ""

# Load configuration
def config_load():
    global config, code_regex
    with open("config.yaml", "r+") as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)

    # Update code regex
    if 'regex' in config['docker']:
        code_regex = re.compile(config['docker']['regex'])
    return config

config_load()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')

if config['package']['debug']:
    logger.setLevel(logging.DEBUG)
    logger.debug("Enabled debugging logs.")

handler = logging.FileHandler(filename='robonev.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Create new client instance
bot = commands.Bot(command_prefix=config['discord']['prefix'])
logger.info(f"Prefix: {config['discord']['prefix']}")

# Pass helpers to bot instance
bot.log = logger
bot.config_load = config_load
bot.config = config

if __name__ == "__main__":
    # Load all default enabled cogs
    for cog in config['extensions']['enabled']:
        try:
            bot.load_extension(cog)
        except:
            logger.error(f"Loading failed for {cog}, traceback:")
            logger.error(traceback.print_exc())


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")


@bot.event
async def on_command_error(ctx, err):
    # TODO: Handle permissions issues
    logger.error(err)

@bot.event
async def on_message(message):
    # Ignore self messages
    if message.author.bot:
        return

    ctx = await bot.get_context(message)
    await bot.invoke(ctx)

    # Regex for code module
    # if 'regex' in config['docker']:
    #     if len(code_regex.findall(message.content)) is not 0:
    #         # Matches git regex, react to it
    #         bot_reaction = await message.add_reaction(config['docker']['code_emoji'])
    #         logger.info(f"Reacting to {message.id}, contains git URL {message.content}")
    #
    #         # Wait 120 seconds for reaction
    #         def check(reaction, user):
    #             return user == message.author and \
    #                    str(reaction.emoji) == config['docker']['code_emoji']
    #
    #         try:
    #             reaction, user = await bot.wait_for('reaction_add', timeout=120.0)
    #         except asyncio.TimeoutError:
    #             # Timed out, remove the reaction
    #             bot_reaction.remove()
    #             return
    #
    #         # User clicked the emoji, call function
    #         ctx = bot.get_context(message)
    #         await ctx.send(f"R. Nev + {config['docker']['code_emoji']}:\nTo create a new"
    #                        f" vs-code server, use the {config['discord']['prefix']}"
    #                        f"code <git url> command.")


bot.run(config['discord']['token'])
