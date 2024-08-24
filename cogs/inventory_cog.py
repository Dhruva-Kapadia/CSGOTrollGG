import discord
from discord.ext import commands
from discord.ui import View, Button
import mysql.connector
from mysql.connector import Error
from db_connect import get_db_connection

class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['i', 'inventory'])
    async def user_inventory(self, ctx):
        try:
            connection = get_db_connection()
            if connection.is_connected():
                cursor = connection.cursor()
                
                # Get user's inventory data
                query = "SELECT inventory_array FROM server_user WHERE user_id = %s AND server_id = %s"
                params = (ctx.author.id, ctx.guild.id)
                cursor.execute(query, params)
                inventory_data = cursor.fetchone()
                
                if inventory_data:
                    inventory_array = inventory_data[0].split(',') if inventory_data[0] else []
                    inventory_array = [int(item) for item in inventory_array if item]  # Convert to integers
                    
                    # Create view with buttons
                    view = View()
                    current_index = 0
                    
                    def create_button(index):
                        return Button(label=f"Skin {index + 1}", style=discord.ButtonStyle.primary)
                    
                    # Add buttons for each skin in inventory
                    for i in range(len(inventory_array)):
                        button = create_button(i)
                        button.callback = lambda button: self.show_skin(ctx, inventory_array, i)
                        view.add_item(button)
                    
                    # Add buttons for previous and next skins
                    view.add_item(Button(label="Previous", style=discord.ButtonStyle.secondary, emoji="⬅️", custom_id="previous"))
                    view.add_item(Button(label="Next", style=discord.ButtonStyle.secondary, emoji="➡️", custom_id="next"))
                    
                    # Send initial message with buttons
                    await ctx.send(f"Your inventory for {ctx.guild.name}:", view=view)
                else:
                    await ctx.send("No skins found in your inventory.")
            else:
                await ctx.send("Failed to connect to MySQL database.")
        except Error as e:
            print(f"Error in inventory command: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    async def show_skin(self, ctx, inventory_array, index):
        try:
            connection = get_db_connection()
            if connection.is_connected():
                cursor = connection.cursor()
                
                # Get skin data from server_skins_inv table
                query = "SELECT skin_id, wear_amount, pattern_id, image_file FROM server_skins_inv WHERE instance_id = %s"
                params = (inventory_array[index],)
                cursor.execute(query, params)
                skin_data = cursor.fetchone()
                
                if skin_data:
                    embed = discord.Embed(title=f"{skin_data[0]}", description=f"Collection: {skin_data[0]}", color=discord.Color.blue())
                    embed.set_thumbnail(url=skin_data[3])
                    
                    # Get skin name from server_skins table (assuming this table exists)
                    query = "SELECT skin_name FROM server_skins WHERE skin_id = %s"
                    params = (skin_data[0],)
                    cursor.execute(query, params)
                    skin_name = cursor.fetchone()
                    
                    embed.set_author(name=f"{ctx.author.name} viewed skin", icon_url=ctx.author.avatar.url)
                    embed.set_footer(text=f"Index: {index + 1}/{len(inventory_array)}")
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Skin data not found.")
            else:
                await ctx.send("Failed to connect to MySQL database.")
        except Error as e:
            print(f"Error showing skin data: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

def setup(bot):
    bot.add_cog(Inventory(bot))
