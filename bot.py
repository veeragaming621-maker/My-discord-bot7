import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename != '__init__.py':
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                logger.info(f'✅ Loaded {filename}')
            except Exception as e:
                logger.error(f'❌ Error loading {filename}: {e}')

@bot.event
async def on_ready():
    logger.info(f'✅ Bot logged in as {bot.user}')
    logger.info(f'✅ Bot is in {len(bot.guilds)} guilds')
    await bot.change_presence(activity=discord.Game(name='!help | Advanced Bot'))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument: {error.param}")
    elif isinstance(error, commands.CommandNotFound):
        return
    else:
        logger.error(f"❌ Error: {error}")

async def main():
    async with bot:
        await load_cogs()
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            raise ValueError("DISCORD_TOKEN not found in .env file")
        await bot.start(token)

if __name__ == '__main__':
    asyncio.run(main())