import discord
from discord import app_commands
from discord.ext import commands


class Format(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    # @app_commands.command(name = 'ping', description = 'just a simple test')
    # async def ping(self, interaction: discord.Interaction):
    #     await interaction.response.send_message('pong')
        
    # @commands.hybrid_command(name = 'ping', description = 'just a simple test')
    # async def ping(self, ctx):
    #     await ctx.reply('Pong')
    
    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if message.author != self.bot.user:
    #         await message.reply('This is a message')


async def setup(bot):
    await bot.add_cog(Format(bot))