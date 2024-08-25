import discord
from discord.ext import commands
import mysql.connector
from user_check import check_user_table
from db_connect import get_db_connection
from mysql.connector import Error
import asyncio


COLOURS = {
            "rarity_common_weapon": 0xb0c3d9,       #Gray
            "rarity_uncommon_weapon": 0x5e98d9,     #Light_Blue
            "rarity_rare_weapon": 0x4b69ff,         #Navy_Blue
            "rarity_mythical_weapon": 0x8847ff,     #Purple
            "rarity_legendary_weapon": 0xd32ce6,    #Pink
            "rarity_ancient_weapon": 0xeb4b4b,      #Red
            "rarity_immortal_weapon": 0xfcba03      #Gold
        }
class Trade(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trade_data = {}
         

    @commands.command(aliases=["tr", "trade"])
    async def trading(self, ctx, target_user: discord.Member, skin_id: str):
        connection = get_db_connection()
        if ctx.author.id == target_user.id:
            await ctx.send("❌ You cannot trade with yourself.")
            return

        # Check if the user owns the skin
        user1_skin = self.get_skin_from_inventory(ctx.author.id, ctx.guild.id, skin_id)
        if not user1_skin:
            await ctx.send(f"❌ You don't own the skin with ID {skin_id}.")
            return
        
        # Prompt the second user to select a skin
        embed = self.create_skin_embed(user1_skin, ctx.author.name)
        await ctx.send(f"{target_user.mention}, which skin would you like to trade?", embed=embed)
        
        def check(m):
            return m.author == target_user and m.content.isdigit() and m.channel == ctx.channel
        
        try:
            response = await self.bot.wait_for('message', check=check, timeout=60.0)
        except asyncio.TimeoutError:
            await ctx.send("❌ Trade request timed out.")
            return
        
        user2_skin = self.get_skin_from_inventory(target_user.id, ctx.guild.id, response.content)
        if not user2_skin:
            await ctx.send(f"{target_user.mention}, you don't own the skin with ID {response.content}.")
            return

        # Confirm trade with user1
        embed = self.create_skin_embed(user2_skin, target_user.name)
        await ctx.send(f"{ctx.author.mention}, do you accept the trade? (y/n)", embed=embed)
        
        def check_confirm(m):
            return m.author == ctx.author and m.content.lower() in ['y', 'yes', 'n', 'no'] and m.channel == ctx.channel
        
        try:
            confirm_response = await self.bot.wait_for('message', check=check_confirm, timeout=60.0)
        except asyncio.TimeoutError:
            await ctx.send("❌ Trade confirmation timed out.")
            return
        
        if confirm_response.content.lower() in ['y', 'yes']:
            await self.finalize_trade(ctx, ctx.author.id, target_user.id, user1_skin['instance_id'], user2_skin['instance_id'])
            await ctx.send("✅ Trade completed successfully!")
        else:
            await ctx.send("❌ Trade was declined.")
    
    def get_skin_from_inventory(self, user_id, guild_id, skin_id):
        try:
            connection = get_db_connection()
            if connection.is_connected():
                cursor = connection.cursor()
                query = "SELECT instance_id, skin_id, Rarity, Skin_Name FROM server_skins_inv WHERE user_id = %s AND server_id = %s AND instance_id = %s"
                cursor.execute(query, (user_id, guild_id, skin_id))
                result = cursor.fetchone()
                if result:
                    return {
                        'instance_id': result[0],
                        'skin_id': result[1],
                        'Rarity': result[2],
                        'Skin_Name': result[3]
                    }
        except Error as e:
            print("Error while connecting to MySQL", e)
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
        return None
    
    def create_skin_embed(self, skin, owner_name):
        embed = discord.Embed(title=f"{skin['Skin_Name']}", description=f"Rarity: {skin['Rarity']}", color=COLOURS.get(skin['Rarity'], 0xffffff))
        embed.set_author(name=f"{owner_name}'s Skin")
        return embed

    async def finalize_trade(self, ctx, user1_id, user2_id, user1_skin_id, user2_skin_id):
        try:
            connection = get_db_connection()
            if connection.is_connected():
                cursor = connection.cursor()

                # Update user1's inventory
                update_user1 = "UPDATE server_skins_inv SET user_id = %s WHERE instance_id = %s"
                cursor.execute(update_user1, (user2_id, user1_skin_id))

                # Update user2's inventory
                update_user2 = "UPDATE server_skins_inv SET user_id = %s WHERE instance_id = %s"
                cursor.execute(update_user2, (user1_id, user2_skin_id))

                connection.commit()
        except Error as e:
            await ctx.send(f"❌ Failed to complete trade: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

def setup(bot):
    bot.add_cog(Trade(bot))
