import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f'Banned {member.mention}')

    @commands.Cog.listener()
    async def on_message(self, message):
        if 'badword' in message.content:
            await message.delete()
            await message.channel.send(f'{message.author.mention}, watch your language!')

async def setup(bot):
    await bot.add_cog(Moderation(bot))
