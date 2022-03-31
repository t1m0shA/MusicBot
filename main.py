# решить проблему с остановкой трека при работе на разных серверах   """RESOLVED"""

# решить проблему очереди при работе на нескольких серверах

# rebuild the queue system

#.play https://www.youtube.com/watch?v=AGkRRdkPTtg&list=PLPf69IGxwfBFdVtuOZ64VlLfmsUb3HRzT
#.play https://www.youtube.com/watch?v=GjMizl3qQGE
#.play https://www.youtube.com/watch?v=K3Min4WnQPw
#.play https://www.youtube.com/watch?v=wNPjimsMNHU
#.play https://www.youtube.com/watch?v=dp-KXWfisHA&list=PLNaZxfoERz7s4sw5fIZX0Dsme5urqRSZr
#.play https://www.youtube.com/watch?v=4s1gBIVOTtk&list=PL6ogdCG3tAWjnVY04Ic42nh6s4tVXAAM6
#.play https://www.youtube.com/watch?v=inybPbfWPjw 



import discord, json, keywords, discord.ext.commands.errors
from discord.ext import commands

cogs = [keywords]
client = commands.Bot(command_prefix='.', intents = discord.Intents.all())

for i in range(len(cogs)): cogs[i].setup(client)

json_file = open('C:/Code/Python/Bots/music_bot/data/commands.json', 'r')
commands_list = json.loads(json_file.read())['SystemResource'] 
json_file.close()

async def embed(ctx, text: str):
        
    """Sends embed message"""

    embed=discord.Embed(
        title='', 
        description = text,
        color=discord.Color.from_rgb(255, 0, 0)
        )
    await ctx.send(embed=embed)

@client.event
async def on_message(message):  
                                
    global container
    if not message.author.bot: container = message.content
    
    if message.author.bot: return

    if not message.content.startswith('.'):
        for item in [*commands_list.values()]:
            if message.content == item[1:]:
                
                embed=discord.Embed(
                    title='', 
                    description = f"Dot prefix needed before assignment. Insert **{item}** to get respond",
                    color=discord.Color.from_rgb(255, 0, 0)
                )
                await message.channel.send(embed=embed)
                return
        else:
            embed=discord.Embed(
                title='', 
                description = f"Invalid command. The message should start with special prefix. Check for available keywords by typing **.commands** in the search bar",
                color=discord.Color.from_rgb(255, 0, 0)
            )
            await message.channel.send(embed=embed)
    await client.process_commands(message)

@client.event
async def on_command_error(ctx, error):
    
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await embed(ctx, text='Command unknown. Check for available keywords by typing **.commands** in the search bar')
       
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument) and ctx.author.voice is not None:
        await embed(ctx, text=f'Command **{container}** requires a parameter')
    
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument) and ctx.author.voice is None:
        await embed(ctx, text=f'You should connect to a voice channel first. The command is missing required argument that depends on keyword you use')

client.run("OTAzNjg1NzkxMTQ0ODk0NTg0.YXwk-g.bXgzrGkvIj8dF5x624DMhOhVGHs")