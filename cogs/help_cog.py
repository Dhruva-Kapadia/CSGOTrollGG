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
        ]

        for command in commands_list:
            embed.add_field(name=f"**{command['name']}**", value=command['description'], inline=False)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(HelpCommand(bot))
