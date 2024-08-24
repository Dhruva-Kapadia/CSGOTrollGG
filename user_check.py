import discord
from discord.ext import commands 
from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error

def check_user_table(ctx, connection):
    try:
        
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        if connection.is_connected():
            cursor = connection.cursor()
            try:
                insert_query = """
                    INSERT INTO server_user (user_id, server_id, rolls, inventory_array, can_claim)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                insert_params = (user_id, guild_id, 0, '', 1)
                cursor.execute(insert_query, insert_params)
                connection.commit()
                
                result = cursor.fetchone()
                
                return result
            except Error as e:
                return
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close() 

                
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None