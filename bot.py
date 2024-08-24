import asyncio
import discord
from discord.ext import commands 
import responses
from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error
import json
import random
from roll_functions import gacha, get_case_data, get_exterior, get_skin_data, get_skin_id_with_condition, has_rolls, insert_skin
from user_check import check_user_table

COLOURS = {
    "rarity_common_weapon": 0xb0c3d9,       #Gray
    "rarity_uncommon_weapon": 0x5e98d9,     #Light_Blue
    "rarity_rare_weapon": 0x4b69ff,         #Navy_Blue
    "rarity_mythical_weapon": 0x8847ff,     #Purple
    "rarity_legendary_weapon": 0xd32ce6,    #Pink
    "rarity_ancient_weapon": 0xeb4b4b,      #Red
    "rarity_immortal_weapon": 0xfcba03      #Gold
}

load_dotenv()

db_config = {
    'host': 'localhost',
    'user': 'csuser',
    'port': 3306,
    'password': 'cs_sucks',
    'database': 'cstroll'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)


def run_discord_bot():
    
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    intents = discord.Intents.all()
    intents.members = True
    intents.guilds = True
    intents.message_content = True
    client = commands.Bot(command_prefix = '>', intents = intents)

    async def reset_can_claim():
        while True:
            try:
                await asyncio.sleep(3600)
                
                connection = mysql.connector.connect(**db_config)
                
                if connection.is_connected():
                    cursor = connection.cursor()
                    cursor.execute("UPDATE server_user SET can_claim = 1 WHERE can_claim = 0")
                    connection.commit()
                else:
                    print("Failed to connect to database")
            except Exception as e:
                print(f"An error occurred: {str(e)}")
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
                    print("Connection closed")

    @client.event
    async def on_ready():
        await client.change_presence(activity=discord.Game(name='>help'))
        print(f'{client.user.name} is running')
        client.loop.create_task(reset_can_claim())

    @client.command(aliases=["hi", "hey"])
    async def hello(ctx):
        connection = get_db_connection()
        check_user_table(ctx, connection)
        await ctx.send(f"Hey there, {ctx.author.mention}!")

    @client.command(aliases = ['timer', 't'])
    async def timers(ctx):
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

        except Error as e:
            print("Error while connecting to MySQL", e)

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    @client.command(aliases=['claim', 'c'])
    async def claims(ctx):
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
        except Error as e:
            print("Error while connecting to MySQL", e)

        
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


    @client.command(aliases=["Roll", "r", "R"])
    async def roll(ctx): 
        owner_id = ctx.author.id
        guild_id = ctx.guild.id
        if has_rolls(owner_id, guild_id):
            skin_id, case_id = gacha()
            skin_data = get_skin_data(skin_id)
            wear = random.uniform(skin_data['Min_wear'], skin_data['Max_wear'])
            condition = get_exterior(wear)
            image_url =get_skin_id_with_condition(skin_id, condition)
            pattern = random.randint(0, 999)
            case_data = get_case_data(case_id)

            insert_skin(skin_id,wear,pattern,owner_id, guild_id, image_url)
            if COLOURS[skin_data['Rarity']]:
                embed_color = COLOURS[skin_data['Rarity']]
            else:
                embed_color = COLOURS["rarity_immortal_weapon"]
            
            if skin_data:
                embed = discord.Embed(title=f"{skin_data['Skin_Name']}", description=f"Collection: {skin_data['collection']}", color = embed_color)
                embed.set_thumbnail(url=skin_data['collection_image_file'])
                embed.add_field(name="Condition", value=condition, inline=True)
                
                embed.set_author(name = f"{ctx.author.name} rolled" ,icon_url=ctx.author.avatar)
                skin_icon_url = image_url        
                embed.set_image(url=skin_icon_url)
                embed.set_footer(text=f"Dropped From {case_data['case_name']}", icon_url=case_data['image_file'])
                
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"No skin found with ID {skin_id}")
        else:
            await ctx.send(f"NO ROLLS, TRY >c")

    @client.event
    async def on_guild_join(guild):
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
            cursor.close()
            db_conn.close()



    client.run(TOKEN)