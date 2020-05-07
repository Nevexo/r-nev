# Commands & cogs for VSCode instances
from discord.ext import commands
from discord.ext.commands import Cog

import aiodocker, asyncio
import random, string

def generate_session_name():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(8))

async def create_session_volume(session):
    docker_client = aiodocker.Docker()
    await docker_client.volumes.create(name=session)
    return

async def create_git_container(image_name, session, git_url):
    docker_client = aiodocker.Docker()
    result = await docker_client.containers.run(image_name, name=f"git-{session}", auto_remove=True,
                      volumes={session: {'bind': '/config/workspace'}},
                      environment=[f"GIT_CLONE_URL={git_url}"])
    # The above is blocking until complete
    result = result.decode('utf-8').replace("\n", "")
    if result == "CLONE_FAIL":
        return False
    else:
        return True

async def create_code_container(session):
    # Launch the vs-code server, returns once started, runs in background.
    container = await docker_client.containers.run("linuxserver/code-server", volumes={
        session: {'bind': "/config/workspace"}
    }, detach=True, auto_remove=True)

    return

class Code(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def clone(self, ctx, *, git_url: str):
        # Create the session name
        session = generate_session_name()
        self.bot.log.info(f"[CODE] Creating new session: {session}")
        # Create session volume
        await create_session_volume(session)
        self.bot.log.info(f"[CODE] Created new session: {session}")
        # Create git clone
        git_result = await create_git_container(self.bot.config['docker']['git_image'],
                                session,
                                git_url)
        self.bot.log.info(f"[CODE] Cloned {git_url}, status: {git_result}")
        if git_result:
            await ctx.send(":white_check_mark: Cloned.")
        else:
            await ctx.send(":x: Failed to clone.")


def setup(bot):
    bot.add_cog(Code(bot))
