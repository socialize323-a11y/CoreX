import discord
from discord.ext import commands
import random

class Leveling(commands.Cog):
    """Leveling system"""
    def __init__(self, bot):
        self.bot = bot
        self.levels = {}
        self.exp = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        user_id = message.author.id
        gain = random.randint(15, 25)
        
        self.exp[user_id] = self.exp.get(user_id, 0) + gain
        level = self.exp[user_id] // 100
        self.levels[user_id] = level

    @commands.command(name='level')
    async def level(self, ctx, member: discord.Member = None):
        """Check your level"""
        member = member or ctx.author
        user_id = member.id
        
        current_exp = self.exp.get(user_id, 0)
        level = self.levels.get(user_id, 0)
        
        embed = discord.Embed(
            title=f"📊 Level - {member}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Level", value=level)
        embed.add_field(name="Experience", value=current_exp)
        await ctx.send(embed=embed)

    @commands.command(name='leaderboard', aliases=['top', 'lb'])
    async def leaderboard(self, ctx):
        """Show level leaderboard"""
        sorted_levels = sorted(self.levels.items(), key=lambda x: x[1], reverse=True)[:10]
        
        embed = discord.Embed(title="🏆 Leaderboard", color=discord.Color.gold())
        
        for i, (user_id, level) in enumerate(sorted_levels, 1):
            try:
                user = await self.bot.fetch_user(user_id)
                embed.add_field(name=f"{i}. {user}", value=f"Level {level}", inline=False)
            except:
                pass
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))
