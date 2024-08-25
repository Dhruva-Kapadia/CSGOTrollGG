import discord
from discord.ext import commands
import mysql.connector
from user_check import check_user_table
from db_connect import get_db_connection

class Trade(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["tr", "trade"])
    async def trade(self, ctx):
        connection = get_db_connection()
        check_user_table(ctx, connection)
        await ctx.send(f"Hey there, {ctx.author.mention}!")

def setup(bot):
    bot.add_cog(Trade(bot))
