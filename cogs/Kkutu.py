import discord
from discord import app_commands
from discord.ext import commands
import json

def load_storage():
    with open ('storage.json') as data:
        return json.load(data)
    
def dump_storage(storage):
    with open('storage.json', 'w') as data:
        json.dump(storage, data)
        return None

class Kkutu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.storage = load_storage()
        self.kkutuChannel = None
        self.wordLimit = 0
        self.count = 0
        
    @commands.Cog.listener()
    async def on_ready(self):
        try:
            self.kkutuChannel = await self.bot.fetch_channel(self.storage['kkutuChannelID'])
        except:
            pass
        try:
            self.wordLimit = self.storage['wordLimit']
        except:
            pass
        
    @commands.hybrid_command(name = 'setkkutuchannel', description = "Set's the channel for KKUTU!!!!!")
    async def setKkutuChannel(self, ctx, id: int):
        self.kkutuChannel = await self.bot.fetch_channel(id)
        self.storage['kkutuChannelID'] = id
        dump_storage(self.storage)
        await ctx.reply(f'<#{id}> is now the Kkutu Channel')
        
    @commands.hybrid_command(name = 'checkkkutuchannel', description = "Check the Kkutu Channel!!!!!")
    async def checkKkutuChannel(self, ctx):
        await ctx.reply(f'The current Kkutu Channel is <#{self.kkutuChannel.id}>')
        
    @commands.hybrid_command(name = 'setwordlimit', description = "Set's the number of words that gets found")
    async def setWordLimit(self, ctx, num: int):
        self.wordLimit = num
        self.storage['wordLimit'] = num
        dump_storage(self.storage)
        await ctx.reply(f'The Word Limit has been changed to {num}')

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author != self.bot.user:
            if ctx.channel == self.kkutuChannel:
                if len(ctx.content) == 1:
                    try:
                        with open(f'words/{ctx.content}.txt', 'r', encoding = 'UTF-8') as f:
                            lines = f.readlines()
                            if lines[0] == 'NONE':
                                await ctx.reply('단어가 존재하지 않습니다')
                                return 0
                            if len(lines) < self.wordLimit:
                                output = [lines[i] for i in range(len(lines))]
                            else:
                                output = [lines[i] for i in range(self.wordLimit)]
                            await ctx.reply(''.join(output))
                    except:
                        await ctx.reply('DB 준비중입니다.....')
                else:
                    await ctx.reply('한 글자만 쳐주세요')
                        
                

        
async def setup(bot):
    await bot.add_cog(Kkutu(bot))