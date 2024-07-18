import discord
from discord.ext import commands

class HelloCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='hello')
    async def hello(self, ctx):
        username = ctx.author.name
        ascii_text = self.text_to_ascii(username)
        await ctx.send(f"```{ascii_text}```")

    def text_to_ascii(self, text):
        ascii_chars = {
            'A': ['  #  ',' # # ','#####','#   #','#   #'],
            'B': ['#### ','#   #','#### ','#   #','#### '],
            'C': [' ####','#    ','#    ','#    ',' ####'],
            'D': ['#### ','#   #','#   #','#   #','#### '],
            'E': ['#####','#    ','#### ','#    ','#####'],
            'F': ['#####','#    ','#### ','#    ','#    '],
            'G': [' ####','#    ','#  ##','#   #',' ####'],
            'H': ['#   #','#   #','#####','#   #','#   #'],
            'I': ['#####','  #  ','  #  ','  #  ','#####'],
            'J': ['#####','    #','    #','#   #',' ### '],
            'K': ['#   #','#  # ','###  ','#  # ','#   #'],
            'L': ['#    ','#    ','#    ','#    ','#####'],
            'M': ['#   #','## ##','# # #','#   #','#   #'],
            'N': ['#   #','##  #','# # #','#  ##','#   #'],
            'O': [' ### ','#   #','#   #','#   #',' ### '],
            'P': ['#### ','#   #','#### ','#    ','#    '],
            'Q': [' ### ','#   #','# # #','#  # ',' ## #'],
            'R': ['#### ','#   #','#### ','#  # ','#   #'],
            'S': [' ####','#    ',' ### ','    #','#### '],
            'T': ['#####','  #  ','  #  ','  #  ','  #  '],
            'U': ['#   #','#   #','#   #','#   #',' ### '],
            'V': ['#   #','#   #','#   #',' # # ','  #  '],
            'W': ['#   #','#   #','# # #','## ##','#   #'],
            'X': ['#   #',' # # ','  #  ',' # # ','#   #'],
            'Y': ['#   #',' # # ','  #  ','  #  ','  #  '],
            'Z': ['#####','   # ','  #  ',' #   ','#####'],
            ' ': ['     ','     ','     ','     ','     '],
        }

        result = ['', '', '', '', '']
        for char in text.upper():
            if char in ascii_chars:
                for i in range(5):
                    result[i] += ascii_chars[char][i] + ' '
            else:
                for i in range(5):
                    result[i] += '     '

        return '\n'.join(result)

async def setup(bot):
    await bot.add_cog(HelloCog(bot))