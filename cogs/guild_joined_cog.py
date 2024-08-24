import discord
from discord.ext import commands
import mysql.connector
from db_connect import get_db_connection

class GuildJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        server_id = str(guild.id)
        server_name = guild.name
        
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        
        try:
            query = "INSERT INTO guilds (server_id, servername) VALUES (%s, %s)"
            values = (server_id, server_name)
            cursor.execute(query, values)
            
            db_conn.commit()  # Commit the transaction
            print(f'Successfully added {server_name} to the database.')
        except Exception as e:
            print(f'Failed to add {server_name} to the database: {e}')
        finally:
            if db_conn.is_connected():
                cursor.close()
                db_conn.close()

def setup(bot):
    bot.add_cog(GuildJoin(bot))
