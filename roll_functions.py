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
from user_check import check_user_table
from db_connect import get_db_connection

def load_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def select_case_from_pool(json_data):
    
    for pool in json_data:
        pool_cases = pool['pool']

        case_ids = [case['id'] for case in pool_cases]
        weights = [case.get('odds', case.get('odd', 0)) for case in pool_cases]
        
        selected_case = random.choices(case_ids, weights=weights, k=1)[0]
        return selected_case, pool['souvenir']
    
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

EXTERIOR_ODDS = (['Factory New', 3, 0, 0.07],
                ['Minimal Wear', 24, 0.07, 0.15], 
                ['Field-Tested', 33, 0.15, 0.38], 
                ['Well-Worn', 24, 0.38, 0.45],
                ['Battle-Scarred', 16, 0.45, 1.00])
    
def select_standard_rarity():   #Rarity choice for standard cases based on odds
    items = list(RARITY_STANDARD.keys())
    weights = list(RARITY_STANDARD.values())
    return random.choices(items, weights, k=1)[0]

def select_souvenir_rarity():   #Rarity choice for souvenir packages based on souvenir odds
    items = list(RARITY_SOUVENIR.keys())
    weights = list(RARITY_SOUVENIR.values())
    return random.choices(items, weights, k=1)[0]

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
        print("Error while connecting to MySQL", e)
        return None
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def generate_wear(skin_data):
    weights = list(x[1] for x in EXTERIOR_ODDS)
    wear = 0

    while(True):
        exterior = random.choices(EXTERIOR_ODDS, weights, k=1)[0]
        print(exterior[0])
        if skin_data['Min_wear'] >= exterior[3] or skin_data['Max_wear'] < exterior[2]:
            continue
        else:
            wear = random.uniform(max(skin_data['Min_wear'], exterior[2]), min(skin_data['Max_wear'], exterior[3]))
            return wear

def get_skin_data(skin_id):
    try:
        connection = get_db_connection()
        
        if connection.is_connected():
            cursor = connection.cursor()
            query_skin = "SELECT Skin_Name, collection_id, Rarity, max_wear, min_wear FROM skins WHERE skin_id = %s"
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
                        'collection': result_2[0], 
                        'collection_image_file': result_2[1], 
                        'Rarity': result_1[2], 
                        'Max_wear': result_1[3], 
                        'Min_wear': result_1[4]
                        }
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

def gacha():
    json_data = load_json_file('./scripts/data/drop_pool.json')
    selected_case, souvenir = select_case_from_pool(json_data)
    
    selected_rarity = ''
    if souvenir:
        selected_rarity = select_souvenir_rarity()
    else:
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

def insert_skin(skin_id, wear, pattern, owner_id, guild_id, image_url):
    try:
        connection = get_db_connection()
        
        if connection.is_connected():
            cursor = connection.cursor()

            sql = """INSERT INTO server_skins_inv (skin_id, wear_amount, pattern_id, user_id, server_id)
                     VALUES (%s, %s, %s, %s, %s)"""
            data = (skin_id, wear, pattern, owner_id, guild_id)
            cursor.execute(sql, data)
            connection.commit()

            last_row_id = cursor.lastrowid

            sql = """UPDATE server_user SET rolls = rolls - 1 WHERE user_id = %s AND server_id = %s"""
            data = (owner_id, guild_id)
            cursor.execute(sql, data)

            sql = """UPDATE server_user SET inventory_array = CONCAT(COALESCE(inventory_array, ''), %s) WHERE user_id = %s AND server_id = %s"""
            inventory_entry = f"{last_row_id},"
            data = (inventory_entry, owner_id, guild_id)
            cursor.execute(sql, data)

            sql = """UPDATE server_skins_inv SET image_file = %s WHERE instance_id = %s"""
            cursor.execute(sql, (image_url, last_row_id))

            connection.commit()
        else:
            print("Error: Unable to connect to MySQL database")
    except mysql.connector.Error as error:
        print(f"Failed to insert skin into server_skins_inv: {error}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()



def has_rolls(owner_id, guild_id):
    try:
        connection = get_db_connection()
        
        if connection.is_connected():
            cursor = connection.cursor()

            sql = """SELECT rolls FROM server_user WHERE user_id = %s AND server_id = %s"""
            data = (owner_id, guild_id)
            cursor.execute(sql, data)

            result = cursor.fetchone()

            if result is not None:
                rolls = result[0]
                return rolls > 0
            else:
                print(f"No entry found for user_id: {owner_id} and server_id: {guild_id}")
                return False
        else:
            print("Error: Unable to connect to MySQL database")
            return False
    except mysql.connector.Error as error:
        print(f"Failed to check rolls: {error}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()