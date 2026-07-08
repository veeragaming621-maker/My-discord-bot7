import discord
from discord.ext import commands
import sqlite3
from datetime import datetime

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('bot.db')
        self.setup_db()

    def setup_db(self):
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY,
                guild_id INTEGER,
                user_id INTEGER,
                channel_id INTEGER,
                message TEXT,
                timestamp DATETIME
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_logs (
                id INTEGER PRIMARY KEY,
                guild_id INTEGER,
                user_id INTEGER,
                action TEXT,
                timestamp DATETIME
            )
        ''')
        self.db.commit()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def chatlogs(self, ctx, member: discord.Member = None, limit: int = 10):
        """View chat logs"""
        member = member or ctx.author
        
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT message, timestamp FROM chat_logs 
            WHERE guild_id = ? AND user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (ctx.guild.id, member.id, limit))
        
        logs = cursor.fetchall()
        
        if not logs:
            await ctx.send(f"❌ No chat logs for {member.mention}")
            return
        
        embed = discord.Embed(title=f"💬 Chat Logs - {member.name}", color=0x0099ff)
        
        for msg, timestamp in logs:
            embed.add_field(name=timestamp, value=msg[:100] + "..." if len(msg) > 100 else msg, inline=False)
        
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def userlogs(self, ctx, member: discord.Member, limit: int = 10):
        """View user logs (joins/leaves)"""
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT action, timestamp FROM user_logs 
            WHERE guild_id = ? AND user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (ctx.guild.id, member.id, limit))
        
        logs = cursor.fetchall()
        
        if not logs:
            await ctx.send(f"❌ No user logs for {member.mention}")
            return
        
        embed = discord.Embed(title=f"👤 User Logs - {member.name}", color=0x00ff00)
        
        for action, timestamp in logs:
            embed.add_field(name=action, value=timestamp, inline=False)
        
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Log messages"""
        if message.author.bot or not message.guild:
            return
        
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO chat_logs (guild_id, user_id, channel_id, message, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (message.guild.id, message.author.id, message.channel.id, message.content, datetime.now()))
        self.db.commit()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Log member joins"""
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO user_logs (guild_id, user_id, action, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (member.guild.id, member.id, "JOINED", datetime.now()))
        self.db.commit()

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Log member leaves"""
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO user_logs (guild_id, user_id, action, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (member.guild.id, member.id, "LEFT", datetime.now()))
        self.db.commit()

async def setup(bot):
    await bot.add_cog(Logs(bot))