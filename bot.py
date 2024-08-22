import discord
from discord.ext import commands 
import responses
from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error

COLOURS = {
    "rarity_common_weapon": 0xb0c3d9,  
    "rarity_uncommon_weapon": 0x4b69ff,
    "rarity_mythical_weapon": 0x8847ff,
    "rarity_legendary_weapon": 0xd32ce6,
    "rarity_ancient_weapon": 0xeb4b4b,
    "Immortal": 0xfcba03
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

def get_skin_data(skin_id):
    try:
        connection = get_db_connection()
        
        if connection.is_connected():
            cursor = connection.cursor()
            query_skin = "SELECT Skin_Name, image_file, collection_id, Rarity FROM skins WHERE skin_id = %s"
            skin_values = (skin_id,)
            cursor.execute(query_skin, skin_values)
            
            result_1 = cursor.fetchone()
            result_2 = []
            
            collection_id = result_1[2]
            
            if collection_id:
                query_collection = "SELECT Collection_Name, image_file FROM collections WHERE collection_id = %s"
                collection_values = (collection_id,)
                cursor.execute(query_collection, collection_values)
                result_2 = cursor.fetchone()
            
            if result_1:
                return {'Skin_Name': result_1[0], 'image_file': result_1[1], 'collection': result_2[0], 'collection_image_file': result_2[1], 'Rarity': result_1[3]}
            else:
                print("No skin found with ID")
                return None
                
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def run_discord_bot():
    
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    intents=discord.Intents.all()
    intents.members = True
    intents.guilds = True
    intents.message_content = True
    client = commands.Bot(command_prefix = '>', intents = intents)

    @client.event
    async def on_ready():
        print(f'{client.user.name} is running')

    @client.command(aliases=["hi", "hey"])
    async def hello(ctx):
        await ctx.send(f"Hey there, {ctx.author.mention}!")

    @client.command(aliases=["Roll", "roll"])
    async def sendembed(ctx):  # Accept skin_id as an argument
        # Fetch skin data from the database
        skin_id="skin-591200"
        skin_data = get_skin_data(skin_id)
        
        if skin_data:
            # Create the embed with dynamic data

            embed = discord.Embed(title=f"{skin_data['Skin_Name']}", description=f"Collection: {skin_data['collection']}", color = COLOURS[skin_data['Rarity']])
            embed.set_thumbnail(url=skin_data['collection_image_file'])
            embed.add_field(name="Skin ID", value=skin_id, inline=True)
            
            # Additional embed setup...
            embed.set_author(name = f"{ctx.author.name} rolled" ,icon_url=ctx.author.avatar)
            skin_icon_url = skin_data['image_file']         
            embed.set_image(url=skin_icon_url)
            embed.set_footer(text="This guy got this", icon_url=ctx.author.avatar)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"No skin found with ID {skin_id}")

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