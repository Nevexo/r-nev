# Commands & cogs for VSCode instances
from discord.ext import commands
from discord.ext.commands import Cog

import aiodocker, asyncio
import random, string
import datetime
import re

docker = aiodocker.Docker()

sessions = {}

def generate_session_name():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(8))


async def create_volume(session):
    """Create the volume for git to clone into"""
    volume = {
        "Name": f"code-{session}"
    }
    vol = await docker.volumes.create(volume)
    return vol


async def git_clone(session, git_url, git_image):
    """Run the git clone instance"""
    container_cfg = {
        "Image": git_image or "git",
        "Env": [
            f"GIT_CLONE_URL={git_url}"
        ],
        "HostConfig": {
            "Mounts": [
                {
                    "Target": "/mnt",
                    "Source": f"code-{session}",
                    "Type": "volume",
                    "ReadOnly": False
                }
            ]
        },
        "AttachStdin": False,
        "AttachStdout": True,
        "AttachStderr": False,
        "Tty": False,
        "OpenStdin": False
    }

    # Launch container
    container = await docker.containers.run(config=container_cfg, name=f"git-{session}")
    # Wait for container to shut down
    await container.wait()
    # Pull result from logs
    result = await container.log(stdout=True)
    # Remove container
    await container.delete()
    # Send clone result to caller (CLONE_OK or CLONE_FAIL)
    return result[0].replace("\n", "")


async def code_container(session):
    """Create code-server container."""
    container_cfg = {
        "Image": "linuxserver/code-server",
        "HostConfig": {
            "Mounts": [
                {
                    "Target": "/config/workspace",
                    "Source": f"code-{session}",
                    "Type": "volume",
                    "ReadOnly": True
                }
            ],
            #"AutoRemove": True,
            "PortBindings": {
                "8443/tcp": [{"HostPort": "8443"}]
            }
        },
        "AttachStdin": False,
        "AttachStdout": False,
        "AttachStderr": False,
        "Tty": False,
        "OpenStdin": False
    }

    container = await docker.containers.run(config=container_cfg,
                                            name=f"code-{session}")

    return container

def check_for_session(userId):
    """Check if a user has an active session"""
    session = None
    for s in sessions:
        s = sessions[s]
        if s['owner'] == userId:
            session = s

    return session

async def tear_down_session(session):
    """Tears down the session from whatever state it's in"""

    if sessions[session]['container'] is not None:
        # Tear down container
        await sessions[session]['container'].stop()
        await sessions[session]['container'].delete()

    if sessions[session]['volume'] is not None:
        # Tear down volume
        await sessions[session]['volume'].delete()

    del sessions[session]

    return

async def create_session_interactive(bot, clone_url, ctx):
    # Create session ID
    status_message = await ctx.send(":clock10: Creating VSCode Instance...")
    msgs = []
    session = generate_session_name()

    sessions[session] = {
        "owner": ctx.author.id,
        "state": "spool_up",
        "url": clone_url
    }

    bot.log.info(f"[GIT] Created new session {session}")
    msgs.append(f"{datetime.datetime.now().isoformat()} - Session {session}"
                f" startup...")

    # Create volume
    volume = await create_volume(session)
    sessions[session]['volume'] = volume
    bot.log.info(f"[GIT] [{session}] Created new volume.")
    msgs.append(f"{datetime.datetime.now().isoformat()} - Volume 'code-{session}"
                f" created.")

    msgs.append(f"{datetime.datetime.now().isoformat()} - Running git container"
                f" git-{session} [cloning {clone_url}]")
    # Create git clone container
    clone_result = await git_clone(session, clone_url, self.bot.config['docker']['git_image'])
    bot.log.info(f"[GIT] [{session}] Clone container shutdown.")

    msgs.append(f"{datetime.datetime.now().isoformat()} - Git container stopped.")

    # Create code-server container
    if clone_result == "CLONE_OK":
        container = await code_container(session)
        sessions[session]['container'] = container
        sessions[session]['state'] = "running"
        msgs.append(f"{datetime.datetime.now().isoformat()} - code-{session} started.")
    else:
        msgs.append(f"{datetime.datetime.now().isoformat()} - Tearing down {session}")
        await tear_down_session(session)
        sessions[session]['state'] = "failed"
        logs = '\n'.join(msgs)
        await ctx.send(":x: Failed to clone git repo, "
                       "please check the url and that the repo"
                       f"is public.\n```{logs}")
        return

    logs = '\n'.join(msgs)
    await status_message.edit(content=f"```{logs}```\nYou can now access your code session"
                                      f" at {self.bot.config['docker']['proxy_proto']}://"
                                      f"code-{session}{self.bot.config['docker']['proxy_base']}")

class Code(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sessions(self, ctx):
        """Get list of active code sessions"""
        msg = "VSC Active Sessions: \n```\nID" \
              "       | Owner ID" \
              "           | Status\n"
        for s in sessions:
            session = sessions[s]
            msg += f"{s} | {session['owner']} | {session['state']}\n"

        msg += "```"

        await ctx.send(msg)

    @commands.command()
    async def delete(self, ctx):
        """Tear down your VS Code session"""
        no_sessions = True

        for session in sessions:
            s = sessions[session]
            if s['owner'] == ctx.author.id and s['state'] == "running":
                msg = await ctx.send(f":clock10: Tearing down {session}")
                await tear_down_session(session)
                await msg.edit(content=f":white_check_mark: {session} torn down.")
                no_sessions = False

        if no_sessions: await ctx.send(":x: You don't have any active sessions.")

    @commands.is_owner()
    @commands.command()
    async def stopAll(self, ctx):
        """Stop all containers"""
        stop_count = 0
        msg = await ctx.send(f"Stopping all containers. {stop_count} stopped so far.")
        for session in sessions:
            await tear_down_session(session)
            stop_count += 1
            await msg.edit(content=f"Stopping all containers. {stop_count} stopped so far.")

    @commands.command()
    async def clone(self, ctx, *, clone_url: str):
        """Clone a Git repo and launch a VS-Code instance."""
        if check_for_session(ctx.author.id):
            await ctx.send(":exclamation: You already have an active "
                           "session, please stop that one first.")
            return

        await create_session_interactive(self.bot, clone_url, ctx)


def setup(bot):
    bot.add_cog(Code(bot))
