import discord
from discord.ext import commands 
import responses
from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error
import json
import random

COLOURS = {
    "rarity_common_weapon": 0xb0c3d9,       #Gray
    "rarity_uncommon_weapon": 0x5e98d9,     #Light_Blue
    "rarity_rare_weapon": 0x4b69ff,         #Navy_Blue
    "rarity_mythical_weapon": 0x8847ff,     #Purple
    "rarity_legendary_weapon": 0xd32ce6,    #Pink
    "rarity_ancient_weapon": 0xeb4b4b,      #Red
    "rarity_immortal_weapon": 0xfcba03      #Gold
}

RARITY_STANDARD = {
        "rarity_rare_weapon": 79.92,            #Navy_Blue
        "rarity_mythical_weapon": 15.98,        #Purple
        "rarity_legendary_weapon": 3.2,         #Pink
        "rarity_ancient_weapon": 0.64,          #Red
#        "rarity_immortal_weapon": 0.26          #Gold
}

RARITY_SOUVENIR = {
        "rarity_common_weapon": 80,             #Gray
        "rarity_uncommon_weapon": 16,           #Light_Blue
        "rarity_rare_weapon": 3.2,              #Navy_Blue
        "rarity_mythical_weapon": 0.64,         #Purple
        "rarity_legendary_weapon": 0.128,       #Pink
        "rarity_ancient_weapon": 0.032          #Red
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

def load_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def select_case_from_pool(json_data):
    
    for pool in json_data:
        pool_cases = pool['pool']

        case_ids = [case['id'] for case in pool_cases]
        weights = [case.get('odds', case.get('odd', 0)) for case in pool_cases]
        
        selected_case = random.choices(case_ids, weights=weights, k=1)[0]
        return selected_case
    
def select_standard_rarity():   #Rarity choice for standard cases based on odds
    items = list(RARITY_STANDARD.keys())
    weights = list(RARITY_STANDARD.values())
    return random.choices(items, weights, k=1)[0]

def select_souvenir_rarity():   #Rarity choice for souvenir packages based on souvenir odds
    items = list(RARITY_SOUVENIR.keys())
    weights = list(RARITY_SOUVENIR.values())
    return random.choices(items, weights, k=1)[0]

def gacha():
    json_data = load_json_file('C:\DKC\CSGOTrollGG\scripts\data\drop_pool.json')
    selected_case = select_case_from_pool(json_data)
    selected_rarity = select_standard_rarity()

    try:
        connection = get_db_connection()

        if connection.is_connected():
            cursor = connection.cursor()
            query_case = "SELECT skin_list FROM cases WHERE case_id = %s"
            selected_case = (selected_case,)
            cursor.execute(query_case, selected_case)

            result = cursor.fetchone()

            if result:
                skins_list = result[0].split(',')
                #Skin choice based on rarity
                
                placeholders = ','.join(['%s'] * len(skins_list))
                query_skins = f"SELECT skin_id FROM skins WHERE skin_id IN ({placeholders}) and Rarity = '{selected_rarity}'"
                cursor.execute(query_skins, skins_list)

                skins_of_selected_rarity = cursor.fetchall()

                return random.choice(skins_of_selected_rarity)[0], selected_case
            else:
                print("No case loaded")
                return None
            
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_skin_data(skin_id):
    try:
        connection = get_db_connection()
        
        if connection.is_connected():
            cursor = connection.cursor()
            query_skin = "SELECT Skin_Name, image_file, collection_id, Rarity FROM skins WHERE skin_id = %s"
            skin_values = (skin_id,)
            cursor.execute(query_skin, skin_values)
            
            result_1 = cursor.fetchone()
            result_2 = ['','']
            
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

def get_case_data(case_id):
    try:
        connection = get_db_connection()
        
        if connection.is_connected():
            cursor = connection.cursor()
            query_case = "SELECT case_name, image_file FROM cases WHERE case_id = %s"
            cursor.execute(query_case, case_id)
            
            result = cursor.fetchone()
            
            if result:
                return {'case_name': result[0], 'image_file': result[1]}
            else:
                print("No case found with ID")
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
    intents = discord.Intents.all()
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

    @client.command(aliases=["Roll", "r"])
    async def roll(ctx):  # Accept skin_id as an argument
        # Fetch skin data from the database
        skin_id, case_id = gacha()
        skin_data = get_skin_data(skin_id)
        case_data = get_case_data(case_id)

        if COLOURS[skin_data['Rarity']]:
            embed_color = COLOURS[skin_data['Rarity']]
        else:
            embed_color = COLOURS["rarity_immortal_weapon"]
        
        if skin_data:
            # Create the embed with dynamic data

            embed = discord.Embed(title=f"{skin_data['Skin_Name']}", description=f"Collection: {skin_data['collection']}", color = embed_color)
            embed.set_thumbnail(url=skin_data['collection_image_file'])
            embed.add_field(name="Skin ID", value=skin_id, inline=True)
            
            # Additional embed setup...
            embed.set_author(name = f"{ctx.author.name} rolled" ,icon_url=ctx.author.avatar)
            skin_icon_url = skin_data['image_file']         
            embed.set_image(url=skin_icon_url)
            embed.set_footer(text=f"Dropped From {case_data['case_name']}", icon_url=case_data['image_file'])
            
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