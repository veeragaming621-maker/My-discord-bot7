import discord
from discord.ext import commands
import sqlite3
from datetime import datetime

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('bot.db')
        self.setup_db()

    def setup_db(self):
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS afk_users (
                guild_id INTEGER,
                user_id INTEGER,
                reason TEXT,
                timestamp DATETIME,
                PRIMARY KEY (guild_id, user_id)
            )
        ''')
        self.db.commit()

    @commands.command()
    async def afk(self, ctx, *, reason="AFK"):
        """Set AFK status"""
        cursor = self.db.cursor()
        cursor.execute('INSERT OR REPLACE INTO afk_users (guild_id, user_id, reason, timestamp) VALUES (?, ?, ?, ?)',
                      (ctx.guild.id, ctx.author.id, reason, datetime.now()))
        self.db.commit()
        
        embed = discord.Embed(title="😴 AFK Status Set", description=f"**Reason:** {reason}", color=0x9900ff)
        await ctx.send(embed=embed)

    @commands.command()
    async def unafk(self, ctx):
        """Remove AFK status"""
        cursor = self.db.cursor()
        cursor.execute('DELETE FROM afk_users WHERE guild_id = ? AND user_id = ?',
                      (ctx.guild.id, ctx.author.id))
        self.db.commit()
        await ctx.send(f"✅ AFK status removed!")

    @commands.command()
    async def afkstatus(self, ctx, member: discord.Member = None):
        """Check if member is AFK"""
        member = member or ctx.author
        
        cursor = self.db.cursor()
        cursor.execute('SELECT reason, timestamp FROM afk_users WHERE guild_id = ? AND user_id = ?',
                      (ctx.guild.id, member.id))
        result = cursor.fetchone()
        
        if not result:
            await ctx.send(f"✅ {member.mention} is not AFK!")
            return
        
        reason, timestamp = result
        embed = discord.Embed(title=f"😴 {member.name} is AFK", description=f"**Reason:** {reason}\n**Since:** {timestamp}", color=0x9900ff)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Alert when AFK member is mentioned"""
        if message.author.bot:
            return
        
        for mention in message.mentions:
            cursor = self.db.cursor()
            cursor.execute('SELECT reason, timestamp FROM afk_users WHERE guild_id = ? AND user_id = ?',
                          (message.guild.id, mention.id))
            result = cursor.fetchone()
            
            if result:
                reason, timestamp = result
                embed = discord.Embed(title=f"😴 {mention.name} is AFK", description=f"**Reason:** {reason}", color=0x9900ff)
                await message.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(AFK(bot))