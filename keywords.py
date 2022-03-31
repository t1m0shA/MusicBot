import discord, json, re, wavelink, asyncio
from wavelink.player import Player
from discord.ext import commands
from youtubesearchpython import *
from threading import Thread
from loop import Queue, Var

class Music(commands.Cog, Player):
    
    def __init__(self, client):
        
        self.client = client
        self.index = 0
        self.queue = {}
        
        self.id = 0
        self._skip = False
        self.stopped = False
        self.permission = False
        self.URL_REG = re.compile(r"https?://(?:www\.)?.+")
        
        if not hasattr(client, 'wavelink'): self.client.wavelink = wavelink.Client(bot=self.client  
        self.client.loop.create_task(self.start_nodes())
                
    async def start_nodes(self):
        
        await self.client.wait_until_ready()
        await self.client.wavelink.initiate_node(
            host='127.0.0.1', 
            port=2333, 
            rest_uri='http://127.0.0.1:2333', 
            password='youshallnotpass', 
            identifier='TEST', 
            region='us_central'
        )    
    async def embed(self, ctx, text: str):
        
        """Sends embed message"""

        embed=discord.Embed(
            title='', 
            description = text,
            color=discord.Color.from_rgb(255, 0, 0)
            )
        await ctx.send(embed=embed)
                                                                                   
    @commands.command(name = "join", aliases = ["j"])
    async def join(self, ctx, *, channel: discord.VoiceChannel = None): 
        
        """Connects the player to a voice channel user is in"""
        print(ctx.author)
        print(ctx.author.guild)
        if self.queue == {}: 
            for server in self.client.guilds: self.queue[server.id] = []
        
        global channel_name
        player = self.client.wavelink.get_player(ctx.guild.id)

        if ctx.author.voice is None: 
            await Music.embed(self, ctx, text = "You are not in voice channel")
        else:
            channel = ctx.author.voice.channel
            await Music.embed(self, ctx, text = f'In channel: **{channel.name}**')
            
        if player.is_connected is None: await player.connect(channel.id)
        else: await player.connect(channel.id)
   
    @commands.command(name = "play", aliases = ["p"])
    async def play(self, ctx, *, query):
        
        """Makes player perform song from provided link or title"""
        #print('queue in play command 1',self.queue,'\n')
        player = self.client.wavelink.get_player(ctx.guild.id)
        if not player.is_connected: await ctx.invoke(self.join)

        query = query.strip("<>")
        if not self.URL_REG.match(query): query = f"ytsearch:{query}"
        #print('queue in play command 2',self.queue,'\n')
        tracks = await self.client.wavelink.get_tracks(query)
        
        if not tracks: await Music.embed(self, ctx, text = "Could not find anything with that query")
        
        if isinstance(tracks, wavelink.TrackPlaylist):
            
            counter = 0
            for track in tracks.tracks:
                
                counter+=1
                self.queue[ctx.guild.id].append([track])
                index = self.queue[ctx.guild.id].index([track])
                
            #gets duration of a song
            #duration is given in milliseconds so it divides it by 1000 to get the value in seconds
                self.queue[ctx.guild.id][index].append(tracks.data['tracks'][tracks.tracks.index(track)]['info']['length']//1000) 
                
            #gets name of a song
                self.queue[ctx.guild.id][index].append(tracks.data['tracks'][tracks.tracks.index(track)]['info']['title']) 
                
            #gets name of a channel song was taken from
                self.queue[ctx.guild.id][index].append(tracks.data['tracks'][tracks.tracks.index(track)]['info']['author']) 
                
            #gets URL of a song
                self.queue[ctx.guild.id][index].append(tracks.data['tracks'][tracks.tracks.index(track)]['info']['uri']) 
                
            #adds 'playlist' type to the end of info set
                self.queue[ctx.guild.id][index].append('Playlist')
        
            self.queue[ctx.guild.id][index].insert(-1, 'Last in playlist')
            playlist_name = tracks.data['playlistInfo']['name']
            #print('queue in play command 3',self.queue,'\n')
            Thread(target=asyncio.run, args=(Queue.runner(self, ctx),)).start()
            await Music.embed(self, ctx, text = f'**{playlist_name}** has been added to the queue as a playlist with {counter} songs')
            
                
        else: 
            
            self.queue[ctx.guild.id].append([tracks[0], tracks[0].length//1000, tracks[0].title, tracks[0].author, tracks[0].uri, 'Single'])

            
            Thread(target=asyncio.run, args=(Queue.runner(self, ctx),)).start()
            
            await Music.embed(self, ctx, text = f'**{tracks[0].title}** has been added to the queue')
    
    @commands.command(name="skip", aliases=["s"])
    async def skip(self, ctx):
        
        """Allows to pass current song"""
        
        player = self.client.wavelink.get_player(ctx.guild.id)
        
        if not player.is_playing: await Music.embed(self, ctx, text = "Music is not playing at all")
        else:
            if len(self.queue[ctx.guild.id]) == 0: await player.stop()
            self._skip = True
        
            

            Thread(target=asyncio.run, args=(Queue.runner(self, ctx),)).start()
            await Music.embed(self, ctx, text = "The song has been skipped and removed from queue")

    @commands.command(name = "next", aliases = ["n"])
    async def next(self, ctx):
        
        """Used to make player skip the whole playlist if one is playing"""
        
        player = self.client.wavelink.get_player(ctx.guild.id)
        
        if not player.is_playing: await Music.embed(self, ctx, text = "Command can't be executed when the player is turned off")
        
        elif Var.current_track[-1] == 'Playlist':
            
        
            container = []
            for i in range(len(self.queue[ctx.guild.id])):
                
                if self.queue[ctx.guild.id][i][-1] == 'Playlist':
                    container.append(i)
                   
                if self.queue[ctx.guild.id][i][-1] != 'Playlist' or 'Last in playlist' in self.queue[ctx.guild.id][i]:
                    
                    break
            
            #print(container)
            del self.queue[ctx.guild.id][min(container):max(container) + 1]
            
            self._skip = True
            if len(self.queue[ctx.guild.id]) == 0: await player.stop()
            Thread(target=asyncio.run, args=(Queue.runner(self, ctx),)).start()
            
            await Music.embed(self, ctx, text = "Current playlist has been skipped and removed from queue")
        
        else: await Music.embed(self, ctx, text = "Current track is not from playlist")
            
    @commands.command()
    async def stop(self, ctx):
        
        """Clears the queue and stops the player"""
        
        player = self.client.wavelink.get_player(ctx.guild.id)
        self.queue[ctx.guild.id].clear()
        await player.stop()
        await Music.embed(self, ctx, text = "The queue has been emptied, all tracks have been removed")
    
    @commands.command()
    async def pause(self, ctx):
        
        """Used to stop song with ability to resume"""

        player = self.client.wavelink.get_player(ctx.guild.id)
        
        if player.is_connected is False and ctx.author.voice is None: 
            await Music.embed(self, ctx, text = "You have to join voice channel to use this command")
        
        elif player.is_connected is False and ctx.author.voice is not None: 
            await Music.embed(self, ctx, text = "Bot is not connected to a voice channel")
        
        elif player.is_connected is not False and ctx.author.voice is None: await Music.embed(self, ctx, text = "You are not connected to a voice channel")
        
        elif player.is_paused: await Music.embed(self, ctx, text = "Song has already been paused")
        
        elif player.is_playing: 
            await player.set_pause(pause=True)
            await Music.embed(self, ctx, text = "Current song is paused")
        
        else: await Music.embed(self, ctx, text = "Player has nothing to cease\nProvide URL or title to play music")
    
    @commands.command()
    async def resume(self, ctx):
        
        """Used to resume song"""

        player = self.client.wavelink.get_player(ctx.guild.id)

        if player.is_connected is False and ctx.author.voice is None: await Music.embed(self, ctx, text = "You have to join voice channel to use this command")
        
        elif player.is_connected is False and ctx.author.voice is not None: 
            await Music.embed(self, ctx, text = "Bot is not in voice channel")
         
        elif player.is_connected is not False and ctx.author.voice is None: await Music.embed(self, ctx, text = "You are not in voice channel")
         
        elif player.is_paused: 
            await player.set_pause(pause=False)
            await Music.embed(self, ctx, text = "Current song is resumed")
        
        elif player.is_playing: await Music.embed(self, ctx, text = "Current song is already playing")
          
        else: await Music.embed(self, ctx, text = "Player has nothing to resume\nProvide URL or title to play music")
          
    @commands.command()
    async def seek(self, ctx, seconds: int):
        
        """Description"""
        
        player = self.client.wavelink.get_player(ctx.guild.id)

        if not player.is_playing and player.is_connected: 
            await Music.embed(self, ctx, text = "Player is currently silent")
        
        elif ctx.author.voice is None: 
            await Music.embed(self, ctx, text = "You are not in voice channel")
         
        elif not player.is_connected: await Music.embed(self, ctx, text = "Player is disconnected from voice channel")
    
        duration = Var.current_track[1]
        
        try:
            if seconds >= duration:
                self._skip = True
        
                if len(self.queue[ctx.guild.id]) == 0: await player.stop()

                Thread(target=asyncio.run, args=(Queue.runner(self, ctx),)).start()
                await Music.embed(self, ctx, text = "Skipped the track entirely")
            else:
                await player.seek(seconds*1000)
                await Music.embed(self, ctx, text = "Rewinded to the given timestamp")
        except:
            pass

    @commands.command(name = "queue", aliases = ["q"])
    async def _queue(self, ctx):

        """Used to display the current queue state"""
       
        text = '1. **' + str(Var.current_track[2]) + '**\n'
        for ind, media in enumerate(self.queue[ctx.guild.id]):
            text += str(ind+2) + '. **' + str(media[2]) + '**\n'

        embed=discord.Embed(
            title="Player's queue", 
            description =str(text),
            color=discord.Color.from_rgb(255, 0, 0)
            )
        
        await ctx.send(embed=embed)

    @commands.command()
    async def commands(self, ctx):
        
        """ Gives a list of available keywords by just taking them from file"""
        
        json_file = open('C:/Code/Python/Bots/music_bot/data/commands.json', 'r')
        Commands = json.loads(json_file.read())['UI']
        json_file.close()
        await Music.embed(self, ctx, text = str("__**Available commands:**__\n \n "+"\n ".join([("**"+str(key) + "**: `" + (str('`; `'.join(val))) +'`') for key, val in Commands.items()])))

def setup(client):
    client.add_cog(Music(client))
