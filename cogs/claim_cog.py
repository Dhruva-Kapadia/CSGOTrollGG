import discord
from discord.ext import commands
import mysql.connector
from db_connect import get_db_connection

class Claims(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['claim', 'c'])
    async def claims(self, ctx):
        server_id = ctx.guild.id
        try:
            connection = get_db_connection()

            if connection.is_connected():
                cursor = connection.cursor()
                query = "SELECT * FROM server_user WHERE user_id = %s AND server_id = %s"
                cursor.execute(query, (ctx.author.id, server_id))
                result = cursor.fetchone()

                if result:
                    can_claim = result[4]
                    rolls = result[2]

                if can_claim != 0:
                    new_rolls = rolls + 10

                    update_query = "UPDATE server_user SET rolls = %s, can_claim = 0 WHERE user_id = %s AND server_id = %s"
                    cursor.execute(update_query, (new_rolls, ctx.author.id, server_id))
                    connection.commit()

                    await ctx.send(f"Congratulations! You've claimed 10 new rolls.")
                    await ctx.send("You can now claim again in 1 hour.")
                else:
                    await ctx.send("You've already claimed today. Try again tomorrow!")
        except mysql.connector.Error as e:
            print(f"Error while connecting to MySQL: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

def setup(bot):
    bot.add_cog(Claims(bot))
