import sys
class Queue():
    
    """ Queue
        ~~~~~~~~~~~~~~~~~~~
        The ultimate custom queue system for wavelink discord bot """
    
    def __init__(self, client):
        
        self.client: client = client
        self.permission: bool = False
        self.current = None
        
    async def stream(self, ctx):
        
        id = ctx.guild.id
        print(1, id)
        player = self.client.wavelink.get_player(ctx.guild.id)
        
        q = self.queue[ctx.guild.id]
        for iter in range(len(q)):
            print('2 in for loop', id)
            iter = 0
            #print('queue in loop',self.queue,"\n")
            while player.is_playing and not self._skip: pass
            else:
                self.permission = True
                self._skip = False

            try:  
                
                if self.permission:
                    print('3 in try ex block', id, '\n')
                    self.current = self.queue[ctx.guild.id][iter]
                    Var.current_track = self.queue[ctx.guild.id][iter]
                    song = self.queue[ctx.guild.id][iter][iter]
                    self.queue[ctx.guild.id].pop(iter)
                    await player.play(song)
                    self.permission = False
            except IndexError:
                pass
        
        #remove in case of issues
        #serves to close thread when the player has went through all tracks in queue
        sys.exit()

    async def runner(self, ctx):
        await Queue.stream(self, ctx)

class Var():
    def __init__(self): self.current_track = None
