import discord
from discord.ext import commands
import mysql.connector
from discord.ext.commands.errors import CommandNotFound
from db_connect import get_db_connection

class Timers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['tu'])
    async def tradeup(self, ctx, *args):
        if len(args)!=10:
            try:
                connection = get_db_connection()
    
                if connection.is_connected():
                    cursor = connection.cursor()
                    query_case = "SELECT can_claim, Rolls FROM server_user WHERE user_id = %s and server_id = %s"
                    params = (ctx.author.id, ctx.guild.id)
                    cursor.execute(query_case, params)
    
                    result = cursor.fetchone()
    
                    if result:
                        if result[0]:
                            await ctx.send(f"You CAN claim now!\nYou currently have {result[1]} rolls left")
                        else:
                            await ctx.send(f"You CANNOT claim now!\nYou currently have {result[1]} rolls left")
                    else:
                        print("No User Found")
    
            except mysql.connector.Error as e:
                print(f"Error while connecting to MySQL: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")
    
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
            
        else:
            await ctx.send('❌ Error: You need exactly 10 items to tradeup!')
            
def setup(bot):
    bot.add_cog(Timers(bot))
