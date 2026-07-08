import discord
from discord.ext import commands
import sqlite3
from datetime import datetime, timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('bot.db')
        self.setup_db()

    def setup_db(self):
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY,
                guild_id INTEGER,
                user_id INTEGER,
                mod_id INTEGER,
                reason TEXT,
                timestamp DATETIME
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mutes (
                id INTEGER PRIMARY KEY,
                guild_id INTEGER,
                user_id INTEGER,
                mod_id INTEGER,
                reason TEXT,
                timestamp DATETIME,
                duration INTEGER
            )
        ''')
        self.db.commit()

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, duration: int = None, *, reason=None):
        """Mute a member"""
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted", color=discord.Color.dark_gray())
        
        await member.add_roles(mute_role)
        embed = discord.Embed(title="✅ Member Muted", description=f"**Member:** {member.mention}\n**Reason:** {reason or 'No reason'}", color=0xff0000)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        """Unmute a member"""
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role and mute_role in member.roles:
            await member.remove_roles(mute_role)
            await ctx.send(f"✅ {member.mention} has been unmuted!")
        else:
            await ctx.send("❌ Member is not muted!")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kick a member"""
        await member.kick(reason=reason or "No reason")
        embed = discord.Embed(title="👢 Member Kicked", description=f"**Member:** {member}\n**Reason:** {reason or 'No reason'}", color=0xff9900)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Ban a member"""
        await member.ban(reason=reason or "No reason")
        embed = discord.Embed(title="🔨 Member Banned", description=f"**Member:** {member}\n**Reason:** {reason or 'No reason'}", color=0xff0000)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        """Unban a member"""
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(f"✅ {user} has been unbanned!")
        except:
            await ctx.send("❌ User not found!")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        """Warn a member"""
        cursor = self.db.cursor()
        cursor.execute('INSERT INTO warnings (guild_id, user_id, mod_id, reason, timestamp) VALUES (?, ?, ?, ?, ?)',
                      (ctx.guild.id, member.id, ctx.author.id, reason or "No reason", datetime.now()))
        self.db.commit()
        await ctx.send(f"⚠️ Warned {member.mention}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int = 10):
        """Purge messages"""
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"✅ Deleted {len(deleted)} messages", delete_after=5)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        """Lock a channel"""
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(f"🔒 {channel.mention} has been locked!")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        """Unlock a channel"""
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(f"🔓 {channel.mention} has been unlocked!")

async def setup(bot):
    await bot.add_cog(Moderation(bot))