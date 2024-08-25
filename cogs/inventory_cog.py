import discord
from discord.ext import commands
from mysql.connector import Error
from db_connect import get_db_connection
import asyncio

COLOURS = {
    "rarity_common_weapon": 0xb0c3d9,       # Gray
    "rarity_uncommon_weapon": 0x5e98d9,     # Light Blue
    "rarity_rare_weapon": 0x4b69ff,         # Navy Blue
    "rarity_mythical_weapon": 0x8847ff,     # Purple
    "rarity_legendary_weapon": 0xd32ce6,    # Pink
    "rarity_ancient_weapon": 0xeb4b4b,      # Red
    "rarity_immortal_weapon": 0xfcba03      # Gold
}

def get_exterior(wear):
    exterior = ''
    if wear < 0.07:
        exterior = 'FN'
    elif wear >= 0.07 and wear < 0.15:
        exterior = 'MW'
    elif wear >= 0.15 and wear < 0.38:
        exterior = 'FT'
    elif wear >= 0.38 and wear < 0.45:
        exterior = 'WW'
    else:
        exterior = 'BS'
    return exterior

class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['i', 'inventory'])
    async def user_inventory(self, ctx, *, member: discord.Member = None):
        if member is None:
            member = ctx.author

        try:
            connection = get_db_connection()
            if connection.is_connected():
                cursor = connection.cursor()

                query = "SELECT inventory_array FROM server_user WHERE user_id = %s AND server_id = %s"
                params = (member.id, ctx.guild.id)
                cursor.execute(query, params)
                inventory_data = cursor.fetchone()

                if inventory_data:
                    inventory_array = inventory_data[0].split(',') if inventory_data[0] else []
                    inventory_array = [int(item) for item in inventory_array if item]

                    if inventory_array:
                        current_index = 0
                        message = await ctx.send(f"{member.display_name}'s inventory for {ctx.guild.name}:")
                        await self.update_inventory_message(message, ctx, inventory_array, current_index, member)

                        await message.add_reaction("⬅️")
                        await message.add_reaction("➡️")

                        def check(reaction, user):
                            return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in ["⬅️", "➡️"]

                        while True:
                            try:
                                reaction, _ = await self.bot.wait_for('reaction_add', timeout=300.0, check=check)

                                if str(reaction.emoji) == "⬅️":
                                    if current_index > 0:
                                        current_index -= 1
                                        await self.update_inventory_message(message, ctx, inventory_array, current_index, member)

                                elif str(reaction.emoji) == "➡️":
                                    if current_index < len(inventory_array) - 1:
                                        current_index += 1
                                        await self.update_inventory_message(message, ctx, inventory_array, current_index, member)

                                await message.remove_reaction(reaction, ctx.author)

                            except asyncio.TimeoutError:
                                await message.clear_reactions()
                                break
                            except Exception as e:
                                print(f"Error handling reactions: {e}")
                                break
                    else:
                        await ctx.send(f"No skins found in {member.display_name}'s inventory.")
                else:
                    await ctx.send(f"No skins found in {member.display_name}'s inventory.")
            else:
                await ctx.send("Failed to connect to MySQL database.")
        except Error as e:
            print(f"Error in inventory command: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    async def update_inventory_message(self, message, ctx, inventory_array, index, member):
        try:
            connection = get_db_connection()
            if connection.is_connected():
                cursor = connection.cursor()

                query = "SELECT skin_id, wear_amount, pattern_id, skin_image_file, Rarity, skin_name, collection_image_file, skin_desc FROM server_skins_inv WHERE instance_id = %s"
                params = (inventory_array[index],)
                cursor.execute(query, params)
                skin_data = cursor.fetchone()
                if skin_data:
                    embed = discord.Embed(title=f"{skin_data[5]} ({get_exterior(skin_data[1])})", description=f"ID: {inventory_array[index]}", color=COLOURS[skin_data[4]])
                    embed.set_thumbnail(url=skin_data[6])
                    embed.add_field(name=f"Float: {skin_data[1]}\nPattern_id: {skin_data[2]}", value=skin_data[7], inline=True)
                    embed.set_image(url=skin_data[3])
                    embed.set_author(name=f"{member.name} viewed skin", icon_url=member.avatar.url)
                    embed.set_footer(text=f"Index: {index + 1}/{len(inventory_array)}")

                    await message.edit(embed=embed, content=f"{member.display_name}'s inventory for {ctx.guild.name}: {index + 1}/{len(inventory_array)}")
                else:
                    await message.edit(content="Skin data not found.")
            else:
                await message.edit(content="Failed to connect to MySQL database.")
        except Error as e:
            print(f"Error updating skin data: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

def setup(bot):
    bot.add_cog(Inventory(bot))
