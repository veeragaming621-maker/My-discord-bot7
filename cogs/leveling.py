import discord
from discord.ext import commands
import sqlite3
import random

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('bot.db')
        self.setup_db()

    def setup_db(self):
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS levels (
                guild_id INTEGER,
                user_id INTEGER,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                PRIMARY KEY (guild_id, user_id)
            )
        ''')
        self.db.commit()

    def get_xp_for_next_level(self, level):
        return 100 * (level ** 1.5)

    @commands.command()
    async def rank(self, ctx, member: discord.Member = None):
        """Show member's rank"""
        member = member or ctx.author
        
        cursor = self.db.cursor()
        cursor.execute('SELECT xp, level FROM levels WHERE guild_id = ? AND user_id = ?',
                      (ctx.guild.id, member.id))
        result = cursor.fetchone()
        
        if not result:
            await ctx.send(f"❌ {member.mention} has no level data!")
            return
        
        xp, level = result
        xp_for_next = self.get_xp_for_next_level(level)
        progress = (xp % int(xp_for_next)) / int(xp_for_next)
        
        progress_bar = "█" * int(progress * 10) + "░" * (10 - int(progress * 10))
        
        embed = discord.Embed(title=f"📊 {member.name}'s Rank", color=0x00ff00)
        embed.add_field(name="Level", value=f"**{level}**", inline=True)
        embed.add_field(name="XP", value=f"**{xp}**", inline=True)
        embed.add_field(name="Progress", value=f"`{progress_bar}` {int(progress*100)}%", inline=False)
        embed.set_thumbnail(url=member.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def leaderboard(self, ctx):
        """Show server leaderboard"""
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT user_id, level, xp FROM levels 
            WHERE guild_id = ?
            ORDER BY level DESC, xp DESC
            LIMIT 10
        ''', (ctx.guild.id,))
        
        results = cursor.fetchall()
        
        if not results:
            await ctx.send("❌ No level data yet!")
            return
        
        embed = discord.Embed(title="🏆 Server Leaderboard", color=0xffff00)
        
        for idx, (user_id, level, xp) in enumerate(results, 1):
            user = self.bot.get_user(user_id)
            medal = ["🥇", "🥈", "🥉"][idx-1] if idx <= 3 else f"{idx}."
            embed.add_field(name=f"{medal} {user or 'Unknown'}", value=f"Level **{level}** - {xp} XP", inline=False)
        
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Award XP on message"""
        if message.author.bot or not message.guild:
            return
        
        cursor = self.db.cursor()
        cursor.execute('SELECT xp, level FROM levels WHERE guild_id = ? AND user_id = ?',
                      (message.guild.id, message.author.id))
        result = cursor.fetchone()
        
        xp = random.randint(5, 15)
        
        if result:
            old_xp, level = result
            new_xp = old_xp + xp
            xp_for_level = self.get_xp_for_next_level(level)
            
            if new_xp >= xp_for_level:
                level += 1
                new_xp -= int(xp_for_level)
                
                embed = discord.Embed(title="🎉 LEVEL UP!", description=f"{message.author.mention} reached **Level {level}**!", color=0x00ff00)
                await message.channel.send(embed=embed)
            
            cursor.execute('UPDATE levels SET xp = ?, level = ? WHERE guild_id = ? AND user_id = ?',
                          (new_xp, level, message.guild.id, message.author.id))
        else:
            cursor.execute('INSERT INTO levels (guild_id, user_id, xp, level) VALUES (?, ?, ?, ?)',
                          (message.guild.id, message.author.id, xp, 1))
        
        self.db.commit()

async def setup(bot):
    await bot.add_cog(Leveling(bot))