import discord
from discord.ext import commands
import random
import mysql.connector
from roll_functions import gacha, generate_wear, get_case_data, get_exterior, get_skin_data, get_skin_id_with_condition, has_rolls, insert_skin

COLOURS = {
            "rarity_common_weapon": 0xb0c3d9,       #Gray
            "rarity_uncommon_weapon": 0x5e98d9,     #Light_Blue
            "rarity_rare_weapon": 0x4b69ff,         #Navy_Blue
            "rarity_mythical_weapon": 0x8847ff,     #Purple
            "rarity_legendary_weapon": 0xd32ce6,    #Pink
            "rarity_ancient_weapon": 0xeb4b4b,      #Red
            "rarity_immortal_weapon": 0xfcba03      #Gold
        }

class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["Roll", "r", "R"])
    async def roll(self, ctx):
        owner_id = ctx.author.id
        guild_id = ctx.guild.id

        if has_rolls(owner_id, guild_id):
            skin_id, case_id = gacha()
            skin_data = get_skin_data(skin_id)
            wear = generate_wear(skin_data)
            condition = get_exterior(wear)
            image_url = get_skin_id_with_condition(skin_id, condition)
            pattern = random.randint(0, 999)
            case_data = get_case_data(case_id)

            insert_skin(skin_id, wear, pattern, condition, owner_id, guild_id, image_url, skin_data['Rarity'], skin_data['Skin_desc'], skin_data['skin_type'], skin_data['collection_id'], skin_data['collection'], skin_data['collection_image_file'] )

            if COLOURS[skin_data['Rarity']]:
                embed_color = COLOURS[skin_data['Rarity']]
            else:
                embed_color = COLOURS["rarity_immortal_weapon"]

            if skin_data:
                embed = discord.Embed(title=f"{skin_data['Skin_Name']}", description=f"Collection: {skin_data['collection']}", color=embed_color)
                embed.set_thumbnail(url=skin_data['collection_image_file'])
                embed.add_field(name="Condition", value=condition, inline=True)

                embed.set_author(name=f"{ctx.author.name} rolled", icon_url=ctx.author.avatar)
                skin_icon_url = image_url
                embed.set_image(url=skin_icon_url)
                embed.set_footer(text=f"Dropped From {case_data['case_name']}", icon_url=case_data['image_file'])

                await ctx.send(embed=embed)
            else:
                await ctx.send(f"No skin found with ID {skin_id}")
        else:
            await ctx.send(f"NO ROLLS, TRY >c")

def setup(bot):
    bot.add_cog(Roll(bot))
