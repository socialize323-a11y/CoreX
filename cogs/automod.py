import discord
from discord.ext import commands

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.automod_settings = {}
        self.spam_tracker = {}
        self.bad_words = [
            'badword1', 'badword2', 'badword3'  # Add actual words
        ]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        guild_id = message.guild.id if message.guild else None
        if not guild_id:
            return
        
        # Check for spam
        await self.check_spam(message)
        
        # Check for bad words
        await self.check_bad_words(message)
        
        # Check for mentions spam
        await self.check_mention_spam(message)

    async def check_spam(self, message):
        """Check for spam messages"""
        guild_id = message.guild.id
        user_id = message.author.id
        
        key = f"{guild_id}_{user_id}"
        
        if key not in self.spam_tracker:
            self.spam_tracker[key] = []
        
        # Add message timestamp
        self.spam_tracker[key].append(message.created_at)
        
        # Keep only messages from last 5 seconds
        import datetime
        now = message.created_at
        self.spam_tracker[key] = [
            ts for ts in self.spam_tracker[key]
            if (now - ts).total_seconds() < 5
        ]
        
        # If more than 5 messages in 5 seconds, it's spam
        if len(self.spam_tracker[key]) > 5:
            try:
                await message.delete()
                await message.channel.send(
                    f"⚠️ {message.author.mention} Please don't spam!",
                    delete_after=5
                )
            except:
                pass

    async def check_bad_words(self, message):
        """Check for bad words"""
        content = message.content.lower()
        
        for word in self.bad_words:
            if word in content:
                try:
                    await message.delete()
                    await message.channel.send(
                        f"⚠️ {message.author.mention} Your message was removed for containing inappropriate content!",
                        delete_after=5
                    )
                except:
                    pass
                break

    async def check_mention_spam(self, message):
        """Check for mention spam"""
        if len(message.mentions) > 5:
            try:
                await message.delete()
                await message.channel.send(
                    f"⚠️ {message.author.mention} Don't mention too many people!",
                    delete_after=5
                )
            except:
                pass

    @commands.command(name='automod')
    @commands.has_permissions(manage_guild=True)
    async def automod(self, ctx, action: str = None):
        """Enable/disable AutoMod"""
        guild_id = ctx.guild.id
        
        if action is None:
            status = self.automod_settings.get(guild_id, False)
            embed = discord.Embed(
                title="🤖 AutoMod Status",
                description=f"AutoMod is {'**Enabled**' if status else '**Disabled**'}",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            return
        
        if action.lower() == 'enable':
            self.automod_settings[guild_id] = True
            embed = discord.Embed(
                title="🤖 AutoMod",
                description="AutoMod has been **enabled**",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        
        elif action.lower() == 'disable':
            self.automod_settings[guild_id] = False
            embed = discord.Embed(
                title="🤖 AutoMod",
                description="AutoMod has been **disabled**",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        
        else:
            await ctx.send("❌ Use 'enable' or 'disable'")

    @commands.command(name='addword')
    @commands.has_permissions(manage_guild=True)
    async def addword(self, ctx, *, word: str):
        """Add a word to the bad words filter"""
        if word not in self.bad_words:
            self.bad_words.append(word.lower())
            await ctx.send(f"✅ Added '{word}' to bad words filter")
        else:
            await ctx.send(f"❌ '{word}' is already in the filter!")

    @commands.command(name='removeword')
    @commands.has_permissions(manage_guild=True)
    async def removeword(self, ctx, *, word: str):
        """Remove a word from bad words filter"""
        if word.lower() in self.bad_words:
            self.bad_words.remove(word.lower())
            await ctx.send(f"✅ Removed '{word}' from bad words filter")
        else:
            await ctx.send(f"❌ '{word}' is not in the filter!")

    @commands.command(name='badwords')
    @commands.has_permissions(manage_guild=True)
    async def badwords(self, ctx):
        """List filtered bad words"""
        embed = discord.Embed(
            title="🚫 Bad Words Filter",
            description=", ".join(self.bad_words) if self.bad_words else "No words filtered",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
