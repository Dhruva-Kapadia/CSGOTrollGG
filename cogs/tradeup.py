import discord
import random
from discord.ext import commands
import mysql.connector
from mysql.connector import Error
from discord.ext.commands.errors import CommandNotFound
from db_connect import get_db_connection

COLOURS = {
            "rarity_common_weapon": 0xb0c3d9,       #Gray
            "rarity_uncommon_weapon": 0x5e98d9,     #Light_Blue
            "rarity_rare_weapon": 0x4b69ff,         #Navy_Blue
            "rarity_mythical_weapon": 0x8847ff,     #Purple
            "rarity_legendary_weapon": 0xd32ce6,    #Pink
            "rarity_ancient_weapon": 0xeb4b4b,      #Red
            "rarity_immortal_weapon": 0xfcba03      #Gold
        }

def get_next_rarity(rarity):
    if rarity == "rarity_common_weapon":
        return "rarity_uncommon_weapon" 
    if rarity == "rarity_uncommon_weapon":
        return "rarity_rare_weapon"
    if rarity == "rarity_rare_weapon":
        return "rarity_mythical_weapon"
    if rarity == "rarity_mythical_weapon":
        return "rarity_legendary_weapon"
    if rarity == "rarity_legendary_weapon":
        return "rarity_ancient_weapon"
    else:
        print("unknown rarity")
        return

def get_skin_id_with_condition(skin_id, condition):
    condition_mapping = {
        'Battle-Scarred': lambda id: id + "_4",
        'Factory New': lambda id: id + "_0",
        'Minimal Wear': lambda id: id + "_1",
        'Field-Tested': lambda id: id + "_2",
        'Well-Worn': lambda id: id + "_3"
    }

    func = condition_mapping.get(condition, lambda id: "Condition not recognized")

    try:
        connection = get_db_connection()
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            skin_image_value = str(func(skin_id))
            
            query_skin_image = "SELECT image_file FROM skin_images where skin_id_ungrouped = %s"
            cursor.execute(query_skin_image, (skin_image_value,))
            
            result = cursor.fetchone()
            return result[0] if result else None
    except Error as e: 
        print("Error while connectingggg to MySQL", e)
        return None
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_exterior(wear):    
    exterior = ''
    if wear<0.07:
        exterior = 'Factory New'
    elif wear>=0.07 and wear<0.15:
        exterior = 'Minimal Wear'
    elif wear>=0.15 and wear<0.38:
        exterior = 'Field-Tested'
    elif wear>=0.38 and wear<0.45:
        exterior = 'Well-Worn'
    else:
        exterior = 'Battle-Scarred'    
    return exterior


def get_skin_data(skin_id):
    try:
        connection = get_db_connection()
        
        if connection.is_connected():
            cursor = connection.cursor()
            query_skin = "SELECT Skin_Name, collection_id, Rarity, max_wear, min_wear, skin_type, Skin_desc FROM skins WHERE skin_id = %s"
            skin_values = (skin_id,)
            cursor.execute(query_skin, skin_values)
            
            result_1 = cursor.fetchone()
            result_2 = ['','']


            collection_id = result_1[1]
            
            if collection_id:
                query_collection = "SELECT collection_name, image_file FROM collections WHERE collection_id = %s"
                collection_values = (collection_id,)
                cursor.execute(query_collection, collection_values)
                result_2 = cursor.fetchone()
            
            if result_1 and result_2:
                return {'Skin_Name': result_1[0],
                        'collection_id': collection_id,
                        'collection': result_2[0], 
                        'collection_image_file': result_2[1], 
                        'Rarity': result_1[2], 
                        'Max_wear': result_1[3],
                        'Min_wear': result_1[4],
                        'skin_type': result_1[5],
                        'Skin_desc': result_1[6],
                        }
            else:
                print("No skin found with ID")
                return None
                
    except Error as e: 
        print("Error while connectin to MySQL", e)
        return None
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def insert_trade_up_skin(skin_id, wear, pattern, condition, owner_id, guild_id, image_url, Rarity, Skin_desc, skin_type, collection_id, collection, collection_image_file):
    try:
        connection = get_db_connection()
        
        if connection.is_connected():
            cursor = connection.cursor()

            sql = """INSERT INTO server_skins_inv (skin_id, wear_amount, pattern_id, `condition`, skin_image_file, Rarity, user_id, server_id, skin_desc, skin_type, collection_id, collection_name, collection_image_file)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            data = (skin_id, wear, pattern, condition, image_url, Rarity, owner_id , guild_id, Skin_desc, skin_type, collection_id, collection, collection_image_file )
            cursor.execute(sql, data)
            connection.commit()

            last_row_id = cursor.lastrowid

            connection.commit()
            return last_row_id
        else:
            print("Error: Unable to connect to MySQL database")
    except mysql.connector.Error as error:
        print(f"Failed to insert skin into server_skins_inv: {error}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

class Tradeup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['tu'])
    async def tradeup(self, ctx, *args):
        if len(args)==10:
            try:
                connection = get_db_connection()

                if connection.is_connected():
                    cursor = connection.cursor()
                    query_inventory = "SELECT inventory_array FROM server_user WHERE user_id = %s and server_id = %s"
                    params = (ctx.author.id, ctx.guild.id)
                    cursor.execute(query_inventory, params)

                    result = cursor.fetchone()
                    #gets user inventory from server_user table to cross verify if the user owns the skins they want to trade up

                    if result:
                        inventory = result[0].split(',')
                    else:
                        await ctx.send('❌ Error: Invalid arguments')
                        return

                    if not all(arg in inventory for arg in args):
                        await ctx.send("❌ Error: You don't own that item!")
                        return
                    
                    query_tradeup_args = "SELECT skin_id, wear_amount, rarity FROM server_skins_inv WHERE instance_id IN (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    params = (args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9])
                    cursor.execute(query_tradeup_args, params)
                    
                    args_result = cursor.fetchall()
                    
                    #gets skin data for user arguments to get the skins and their rarity

                    rarity_set = [i[2] for i in args_result]
                    if not len(set(rarity_set)) == 1:               
                        #prevents tradeup from items of different rarities
                        await ctx.send('❌ Error: All items need to be of the same rarity')
                        return
                    
                    if rarity_set[0] == 'rarity_ancient_weapon':    
                        #prevents trading up from max rarity
                        await ctx.send('❌ Error: These items are already of max rarity. You cannot tradeup from these anymore')
                        return

                    skin_id_for_collection = random.choice(args_result)[0]  
                    #RNG choose skin for choosing collection

                    query_tradeup_collection = "SELECT collection_id from skins where skin_id = %s"
                    cursor.execute(query_tradeup_collection, (skin_id_for_collection,))
                    
                    tradeup_collection = cursor.fetchone()[0]
                    #RNG collection chosen
                    
                    new_rarity = get_next_rarity(rarity_set[0])
                    #Gets the next rarity from current rarity

                    query_tradeup_skin = "SELECT skin_id FROM skins WHERE collection_id = %s AND Rarity = %s"
                    params = (tradeup_collection, new_rarity)
                    cursor.execute(query_tradeup_skin, params)
                    skins_result = cursor.fetchall()
                    #Fetches all skins from the selected collection with the next rarity 

                    final_skin = random.choice(skins_result)[0]
                    #Chooses the final skin from the resultant list of skins

                    skin_data = get_skin_data(final_skin)

                    wear_list = [row[1] for row in args_result]
                    wear = sum(wear_list)/10
                    #NOTE: Wear logic to be updated for non standard min and max wear values
                    
                    condition = get_exterior(wear)
                    pattern = random.randint(0,999)
                    owner_id = ctx.author.id
                    guild_id = ctx.guild.id
                    image_url = get_skin_id_with_condition(final_skin, condition)

                    new_skin_id = insert_trade_up_skin(final_skin, wear, pattern, condition,  image_url, new_rarity, owner_id, guild_id, skin_data['Skin_desc'], skin_data['skin_type'], skin_data['collection_id'], skin_data['collection'], skin_data['collection_image_file'])

                    if new_skin_id:
                        updated_inventory = [item for item in inventory if item and item not in args]
                        updated_inventory.append(str(new_skin_id))
                        updated_inventory_str = ','.join([item for item in updated_inventory if item])
                        query_update_inventory = "UPDATE server_user SET inventory_array = %s WHERE user_id = %s AND server_id = %s"
                        cursor.execute(query_update_inventory, (updated_inventory_str, owner_id, guild_id))

                        query_delete_skins = "DELETE FROM server_skins_inv WHERE instance_id IN (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        cursor.execute(query_delete_skins, args)

                        connection.commit()

                    await ctx.send('✅ Trade-up successful! Enjoy your new skin.')

                    if COLOURS[skin_data['Rarity']]:
                        embed_color = COLOURS[skin_data['Rarity']]
                    else:
                        embed_color = COLOURS["rarity_immortal_weapon"]
                    #Colour selection
                    if skin_data:
                        embed = discord.Embed(title=f"{skin_data['Skin_Name']}", description=f"Collection: {skin_data['collection']}", color=embed_color)
                        embed.set_thumbnail(url=skin_data['collection_image_file'])
                        embed.add_field(name="Condition", value=condition, inline=True)

                        embed.set_author(name=f"{ctx.author.name} rolled", icon_url=ctx.author.avatar)
                        skin_icon_url = image_url
                        embed.set_image(url=skin_icon_url)

                        await ctx.send(embed=embed)
                    else:
                        await ctx.send(f"No skin found with ID {final_skin}")
                    #Display embed after tradeup                    

            except mysql.connector.Error as e:
                print(f"Error while connecti to MySQL: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")

            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
            
        else:
            await ctx.send('❌ Error: You need exactly 10 items to tradeup!')
            
def setup(bot):
    bot.add_cog(Tradeup(bot))
