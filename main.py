import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os
from cogs.Kkutu import Kkutu
from cogs.music import Music


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix = '=', intents = discord.Intents.all(), application_id = '1316958087114133566')
    
    async def setup_hook(self):
        fmt = await self.tree.sync()
        print(fmt)
        
bot = MyBot()

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            
asyncio.run(load())

with open('token.txt') as token:
    bot.run(token.readline())