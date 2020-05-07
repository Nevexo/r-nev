# r.nev 3.0, a utility bot.

import discord
import traceback
import yaml
from discord.ext import commands
import logging, logging.handlers

config = {}


# Load configuration
def config_load():
    global config
    with open("config.yaml", "r+") as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)

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


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")


@bot.event
async def on_command_error(ctx, err):
    logger.error(err)


bot.run(config['discord']['token'])
