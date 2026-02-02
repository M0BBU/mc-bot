import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from string import Template

import os
import time
import logging
import traceback
import asyncio

from .provider import gcp
from .server import servers

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

PROJECT_ID = os.getenv("PROJECT_ID")
ZONE = os.getenv("ZONE")
SERVER = os.getenv("SERVER")

SSH_USER = os.getenv("SSH_USER")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH")

CF_API_KEY = os.getenv("CF_API_KEY")

WHITELIST = os.getenv("WHITELIST")

DOCKER_TEMPLATE_CMD = Template(r"""sudo docker run \
    -d \
    -it \
    -p 25565:25565 \
    -e EULA=TRUE \
    -e MOD_PLATFORM=AUTO_CURSEFORGE \
    -e CF_API_KEY=$cf_api_key \
    -e CF_SLUG=$cf_slug \
    -e MEMORY=4G \
    -e ENABLE_WHITELIST=true \
    -e WHITELIST=$whitelist \
    -v ~/mcworlds/$server:/data \
    itzg/minecraft-server:java21 """)

@bot.event
async def on_ready() -> None:
    logger.info(f'Logged in as {bot.user}')

@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return

    logger.info(f'recieved {message.content} from {message.author}')

    await bot.process_commands(message)

@bot.command(brief="Starts minecraft server.")
async def startserver(ctx, name: str) -> None:
    # clean up the input a bit so that we don't have spaces in our keys.
    name = name.replace(" ", "-")
    await ctx.send(f"Starting server {name}, please wait!")
    await asyncio.to_thread(gcp.start_instance, logger, PROJECT_ID, ZONE, SERVER)

    ips = await asyncio.to_thread(gcp.get_instance_ipv4, logger, PROJECT_ID, ZONE, SERVER)
    numIPs = len(ips)
    if numIPs != 1:
        logger.warn(f"unexpected number of IP(s) found: {ips}")
        raise RuntimeError(f"Expected one IP address but found {numIPs}")

    servers.run_server(name, logger, ips[0], SSH_USER, SSH_KEY_PATH)
    
    embed = discord.Embed(title=f"Successfully started `{name}`!",
                          description=f"IP address: `{ips[0]}`")
    await ctx.send(embed=embed)

    return

@bot.command(brief="Gets all minecraft servers.")
async def getservers(ctx) -> None:
    mcservers = servers.get_servers()

    embed = discord.Embed(
        title="Minecraft Server List",
        description="List of minecraft servers",
        color=discord.Color.green()
    )
    server_names = "\n".join([f"`{name}`" for name in mcservers.keys()])
    embed.add_field(name="Servers", value=server_names, inline=False)

    await ctx.send(embed=embed)
    return

@bot.command(brief="Creates a new minecraft server.")
async def addserver(ctx,
                    name: str=commands.parameter(default="", description="Name of minecraft server"),
                    modpack: str=commands.parameter(default="", description="Optional modpack. Ex: cobblemon-neoforge."),
) -> None:
    if name == "":
        await ctx.send(f"HEY! You need to specify a name for the server!")
        return 

    # clean up the input a bit so that we don't have spaces in our keys.
    name = name.replace(" ", "-")
    command = DOCKER_TEMPLATE_CMD.substitute(
        cf_api_key=CF_API_KEY,
        cf_slug=modpack,
        server=name,
        whitelist=WHITELIST,
    )
    if not servers.save_server(name, command, logger):
        await ctx.send(f"HEY! `{name}` is already a server!")
        return 
        
    embed = discord.Embed(title=f"Successfully created new server {name}!",
                          description=f"Run `!startserver \"{name}\"` to use it.")
    await ctx.send(embed=embed)
    return

@bot.command(brief="Stops all minecraft server.")
async def stopserver(ctx) -> None:
    await ctx.send("Shutting down server...")
    await asyncio.to_thread(gcp.stop_instance, logger, PROJECT_ID, ZONE, SERVER)

    embed = discord.Embed(title="Shut down server!")
    await ctx.send(embed=embed)
    return

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    embed = discord.Embed(title="Error")
    error_data = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    embed.description = f"Unknown error\n```py\n{error_data[:1000]}\n```"
    await ctx.send(embed=embed)

bot.run(os.getenv("DISCORD_TOKEN"))
