import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

import os
import time
import logging
import traceback
import asyncio

import gcp

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
async def startserver(ctx) -> None:
    await ctx.send("Starting server, please wait!")
    await asyncio.to_thread(gcp.start_instance, logger, PROJECT_ID, ZONE, SERVER)
    ips = await asyncio.to_thread(gcp.get_instance_ipv4, logger, PROJECT_ID, ZONE, SERVER)
    numIPs = len(ips)
    if numIPs != 1:
        logger.warn(f"unexpected number of IP(s) found: {ips}")
        raise RuntimeError(f"Expected one IP address but found {numIPs}")

    embed = discord.Embed(title="Successfully started server!",
                          description=f"IP address: `{ips[0]}`")
    await ctx.send(embed=embed)
    return

@bot.command(brief="Stops minecraft server.")
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
