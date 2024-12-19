import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import yt_dlp
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import json
from youtubesearchpython import VideosSearch

# https://github.com/pawel02/music_bot/blob/main/music_cog.py

def load_musicChannels():
    with open ('musicChannels.json') as data:
        return json.load(data)
    
def dump_musicChannels(storage):
    with open('musicChannels.json', 'w') as data:
        json.dump(storage, data)
        return None
    
def load_musicMessages():
    with open ('musicMessages.json') as data:
        return json.load(data)
    
def dump_musicMessages(storage):
    with open('musicMessages.json', 'w') as data:
        json.dump(storage, data)
        return None



class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        load_dotenv()
        self.yt_dl_options = {'format': 'bestaudio/best'}
        self.ytdl = yt_dlp.YoutubeDL(self.yt_dl_options)
        self.ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.03"'}
        
        self.musicChannels = load_musicChannels()   # Uses musicChannels.json
        self.musicMessages = load_musicMessages()
        self.titleQueues = {}
        self.urlQueues = {}
        self.voice_clients = {}
        self.voiceChannels = {}
        self.isPlaying = {}
        self.nowPlaying = {}    #Receive only the title of the song, probably url is not needed
        
        
    @commands.Cog.listener()
    async def on_ready(self):
        for guildID in self.musicChannels.keys():
            self.isPlaying[int(guildID)] = False
            self.nowPlaying[int(guildID)] = ''
            self.voiceChannels[int(guildID)] = 0
        print("Bot is now ready")
        
    async def updateEmbed(self, ctx):
        embed = discord.Embed(title = self.nowPlaying[ctx.guild.id], color = 0xD5C171)
        newQueue = [str(i+1) + '. ' + title for i, title in enumerate(self.titleQueues[ctx.guild.id])]
        embed.add_field(name = 'Queue', value = '\n'.join(newQueue))
        embed.set_image(url = 'https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/d6f05f67-f286-4332-a2e7-55d7fe3e05cf/d8u2ob5-5ae920c0-de6f-4436-bef0-98e667e425e3.png/v1/fit/w_800,h_781,q_70,strp/449___hippopotas_by_onixtymime_d8u2ob5-414w-2x.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9NzgxIiwicGF0aCI6IlwvZlwvZDZmMDVmNjctZjI4Ni00MzMyLWEyZTctNTVkN2ZlM2UwNWNmXC9kOHUyb2I1LTVhZTkyMGMwLWRlNmYtNDQzNi1iZWYwLTk4ZTY2N2U0MjVlMy5wbmciLCJ3aWR0aCI6Ijw9ODAwIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmltYWdlLm9wZXJhdGlvbnMiXX0.KnnTQ96Y3qHr4hxAl-1SDDhdbVovLGGUbED6ZVB6xx8')
        channel = await self.bot.fetch_channel(self.musicChannels[str(ctx.guild.id)])
        msg = await channel.fetch_message(self.musicMessages[str(ctx.guild.id)])
        await msg.edit(embed=embed)
    
    async def mainEmbed(self, ctx):
        embed = discord.Embed(title = 'HIPPOPOTAS is waiting......', color = 0xD5C171)
        embed.set_image(url = 'https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/d6f05f67-f286-4332-a2e7-55d7fe3e05cf/d8u2ob5-5ae920c0-de6f-4436-bef0-98e667e425e3.png/v1/fit/w_800,h_781,q_70,strp/449___hippopotas_by_onixtymime_d8u2ob5-414w-2x.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9NzgxIiwicGF0aCI6IlwvZlwvZDZmMDVmNjctZjI4Ni00MzMyLWEyZTctNTVkN2ZlM2UwNWNmXC9kOHUyb2I1LTVhZTkyMGMwLWRlNmYtNDQzNi1iZWYwLTk4ZTY2N2U0MjVlMy5wbmciLCJ3aWR0aCI6Ijw9ODAwIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmltYWdlLm9wZXJhdGlvbnMiXX0.KnnTQ96Y3qHr4hxAl-1SDDhdbVovLGGUbED6ZVB6xx8')
        channel = await self.bot.fetch_channel(self.musicChannels[str(ctx.guild.id)])
        msg = await channel.fetch_message(self.musicMessages[str(ctx.guild.id)])
        await msg.edit(embed=embed)
        
    @commands.hybrid_command(name = 'play', description = 'Play Music')
    async def play(self, ctx):
            
        try:
            vc = await ctx.author.voice.channel.connect(self_deaf=True)
            self.voice_clients[vc.guild.id] = vc
            self.voiceChannels[ctx.guild.id] = ctx.author.voice.channel.id
        except Exception as e:
            print(e)
            
        if self.urlQueues[ctx.guild.id] != []:
            url = self.urlQueues[ctx.guild.id].pop(0)  
            title = self.titleQueues[ctx.guild.id].pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(url, download = False))
            
            song = data['url']
            player = discord.FFmpegOpusAudio(song, **self.ffmpeg_options)
            
            self.isPlaying[ctx.guild.id] = True
            self.nowPlaying[ctx.guild.id] = title
            await self.updateEmbed(ctx)
            
            self.voice_clients[ctx.guild.id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(self.play(ctx), self.bot.loop))
            
        else:
            self.isPlaying[ctx.guild.id] = False
            self.nowPlaying[ctx.guild.id] = ''
            await self.mainEmbed(ctx)
            
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author != self.bot.user and message.channel.id == self.musicChannels[str(message.guild.id)]:
            await message.delete()
            if 'youtube' in message.content:
                await self.addToQueue(message, message.content)
            else:
                await message.channel.send("Please input a youtube link", delete_after=3)


            
    async def addToQueue(self, ctx, url):  #If song is already playing -> Add the song to the queue
        # Create a list if it doeesn't exist'
        
        # Check if member is in a voice channel
        if ctx.author.voice == None:
            await ctx.channel.send('Input after you join a Voice Channel', delete_after=3)
            return 0
        if (ctx.guild.id not in self.voiceChannels or ctx.author.voice.channel.id != self.voiceChannels[ctx.guild.id]) and self.isPlaying[ctx.guild.id] == True:
            await ctx.channel.send('Hippopotas is already singing in another channel', delete_after=3)
            return 0
        
        try:
            if ctx.author.voice.channel.id != self.voiceChannels[ctx.guild.id]:
                await self.voice_clients[ctx.guild.id].disconnect()
        except:
            pass
            
        
        # Create a new list if a queue doesn't exist
        if ctx.guild.id not in self.urlQueues:
            self.urlQueues[ctx.guild.id] = []
        if ctx.guild.id not in self.titleQueues:
            self.titleQueues[ctx.guild.id] = []
        
        # Append url and title to queue
        if url.startswith('https://'):
            title = self.getTitle(url)
            self.urlQueues[ctx.guild.id].append(url)
            self.titleQueues[ctx.guild.id].append(title)
        else:
            search = VideosSearch(url, limit = 1)
            url = search.result()['result'][0]['link']
            title = search.result()['result'][0]['title']
            self.urlQueues[ctx.guild.id].append(url)
            self.titleQueues[ctx.guild.id].append(title)
    
        await self.updateEmbed(ctx)

        
        # If bot is not playing, Start playing
        if self.isPlaying[ctx.guild.id] == False:
            await self.play(ctx)
            
    @commands.hybrid_command(name = 'clearqueue', description = 'Clear the Queue')
    async def clearQueue(self, ctx):
        if ctx.guild.id in self.urlQueues:
            self.urlQueues[ctx.guild.id].clear()
            self.titleQueues[ctx.guild.id].clear()
            await self.updateEmbed(ctx)
            await ctx.send('Queue Cleared', ephemeral = True, delete_after=3)
        else:
            await ctx.send("Queue doesn't exist", ephemeral=True, delete_after=3)
            
    @commands.hybrid_command(name = 'setmusicchannel', description = 'Set your own Music Channel!', aliases = ['setMusicChannel'])
    async def setMusicChannel(self, ctx, id: str):
        try:
            channel = await self.bot.fetch_channel(int(id))
        except:
            print("Couldn't set Music Channel because channel was not found")
            await ctx.reply('Channel was not found')
            return 0
        self.musicChannels[str(ctx.guild.id)] = int(id)
        dump_musicChannels(self.musicChannels)
        self.isPlaying[ctx.guild.id] = False
        self.nowPlaying[ctx.guild.id] = ''
                                           
        mainEmbed = discord.Embed(title = 'Wild HIPPOPOTAS appeared!                                  ', color = 0xD5C171)
        mainEmbed.set_image(url = 'https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/d6f05f67-f286-4332-a2e7-55d7fe3e05cf/d8u2ob5-5ae920c0-de6f-4436-bef0-98e667e425e3.png/v1/fit/w_800,h_781,q_70,strp/449___hippopotas_by_onixtymime_d8u2ob5-414w-2x.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9NzgxIiwicGF0aCI6IlwvZlwvZDZmMDVmNjctZjI4Ni00MzMyLWEyZTctNTVkN2ZlM2UwNWNmXC9kOHUyb2I1LTVhZTkyMGMwLWRlNmYtNDQzNi1iZWYwLTk4ZTY2N2U0MjVlMy5wbmciLCJ3aWR0aCI6Ijw9ODAwIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmltYWdlLm9wZXJhdGlvbnMiXX0.KnnTQ96Y3qHr4hxAl-1SDDhdbVovLGGUbED6ZVB6xx8')
        
        msg = await channel.send(embed = mainEmbed)
        self.musicMessages[str(ctx.guild.id)] = msg.id
        dump_musicMessages(self.musicMessages)
        
    @commands.hybrid_command(name = 'remove', description = 'Remove Music from Queue')
    async def remove(self, ctx, index: int):
        self.urlQueues[ctx.guild.id].pop(index-1)
        title = self.titleQueues[ctx.guild.id].pop(index-1)
        
        await self.updateEmbed(ctx)
        await ctx.send(f"Removed **{title}** from Queue", ephemeral = True, delete_after = 3)
        
    @commands.hybrid_command(name = 'skip', description = 'Skip this Song')
    async def skip(self, ctx):
        if self.voice_clients[ctx.guild.id] != None and self.isPlaying[ctx.guild.id] == True:
            self.voice_clients[ctx.guild.id].stop()
            await ctx.send('Skipped', ephemeral=True, delete_after=3)
        
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id == 1316958087114133566:
            print(before.channel, after.channel)
            if before.channel != None and after.channel == None:
                self.urlQueues[member.guild.id].clear()
                self.titleQueues[member.guild.id].clear()
                self.isPlaying[member.guild.id] = False
                self.nowPlaying[member.guild.id] = ''
                self.voiceChannels[member.guild.id] = 0
                self.voice_clients[member.guild.id] = None
                await self.mainEmbed(member)
        
    def getTitle(self, url):
        if 'music.youtube.com' in url:
            url = url[:8] + url[14:]
        res = requests.get(url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'lxml')
        
        data = soup.find(name='title')
        title = data.text
        return title[:-10]

            
        
    # def getThumbnail(self, url):
    #     res = requests.get(url)
    #     res.raise_for_status()
    #     soup = BeautifulSoup(res.text, 'lxml')
    #     if 'music.youtube.com' in url:
    #         data = soup.find_all('img')
    #         print(data)
    #         return data.get('src')
    #     else:
    #         data = soup.find('link', {'itemprop': 'thumbnailUrl'})
    #         print(data.get('href'))
    #         return data.get('href')
            
        
    # @commands.hybrid_command(name = 'sync', description = 'Sync the Slash Commands')
    # async def sync(self, ctx):
    #     print('syncing...')
    #     fmt = await ctx.bot.tree.sync()
    #     await ctx.reply(f'Synced {len(fmt)} commands to the current guild')
        
async def setup(bot):
    await bot.add_cog(Music(bot))