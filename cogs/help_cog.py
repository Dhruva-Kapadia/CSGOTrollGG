import discord
from discord.ext import commands

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['h'])
    async def help_command(self, ctx):
        embed = discord.Embed(title="Help Menu", color=discord.Color.blue())

        commands_list = [
            {"name": "hi", "description": "Register yourself to interact with the bot"},
            {"name": "c, claim", "description": "Claim 10 rolls every hour"},
            {"name": "t, timer", "description": "Check your claim status and remaining rolls"},
            {"name": "r, R, roll", "description": "Roll to get one of the skins from CS"},
            {"name": "tu", "description": "insert any 10 skins of the same rarity and get one higer rarity skin"},
            {"name": "tr", "description": "trade with any member using the instance of the skin(>tr @mention 1(id))"},
            {"name": "i", "description": "see your invetory or mention to see the mentioned user's inventory"},
        ]

        for command in commands_list:
            embed.add_field(name=f"**{command['name']}**", value=command['description'], inline=False)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(HelpCommand(bot))
