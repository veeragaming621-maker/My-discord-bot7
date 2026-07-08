import discord
from discord.ext import commands
import sqlite3
from datetime import datetime, timedelta
import random

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('bot.db')
        self.setup_db()

    def setup_db(self):
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS giveaways (
                id INTEGER PRIMARY KEY,
                guild_id INTEGER,
                channel_id INTEGER,
                message_id INTEGER,
                prize TEXT,
                end_time DATETIME,
                winners INTEGER,
                created_by INTEGER,
                status TEXT
            )
        ''')
        self.db.commit()

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def giveaway(self, ctx):
        """Giveaway system commands"""
        embed = discord.Embed(title="🎁 Giveaway System", color=0xff00ff)
        embed.add_field(name="!giveaway create", value="Create a giveaway", inline=False)
        embed.add_field(name="!giveaway end <message_id>", value="End a giveaway", inline=False)
        embed.add_field(name="!giveaway reroll <message_id>", value="Reroll winners", inline=False)
        await ctx.send(embed=embed)

    @giveaway.command(name='create')
    @commands.has_permissions(administrator=True)
    async def create_giveaway(self, ctx):
        """Create a giveaway interactively"""
        
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        
        await ctx.send("What channel should the giveaway be in?")
        channel_msg = await self.bot.wait_for('message', check=check, timeout=30)
        
        try:
            channel = await commands.TextChannelConverter().convert(ctx, channel_msg.content)
        except:
            await ctx.send("❌ Invalid channel!")
            return
        
        await ctx.send("What is the prize?")
        prize_msg = await self.bot.wait_for('message', check=check, timeout=30)
        prize = prize_msg.content
        
        await ctx.send("How many winners?")
        winners_msg = await self.bot.wait_for('message', check=check, timeout=30)
        
        try:
            winners = int(winners_msg.content)
        except:
            await ctx.send("❌ Invalid number!")
            return
        
        embed = discord.Embed(title="🎁 GIVEAWAY", description=f"Prize: **{prize}**\nWinners: **{winners}**", color=0xff00ff)
        embed.set_footer(text="React with 🎉 to enter!")
        
        msg = await channel.send(embed=embed)
        await msg.add_reaction("🎉")
        
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO giveaways (guild_id, channel_id, message_id, prize, winners, created_by, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (ctx.guild.id, channel.id, msg.id, prize, winners, ctx.author.id, 'active'))
        self.db.commit()
        
        await ctx.send(f"✅ Giveaway created!")

    @giveaway.command(name='end')
    @commands.has_permissions(administrator=True)
    async def end_giveaway(self, ctx, message_id: int):
        """End a giveaway and select winners"""
        cursor = self.db.cursor()
        cursor.execute('SELECT channel_id, prize, winners FROM giveaways WHERE message_id = ?', (message_id,))
        result = cursor.fetchone()
        
        if not result:
            await ctx.send("❌ Giveaway not found!")
            return
        
        channel_id, prize, num_winners = result
        channel = self.bot.get_channel(channel_id)
        
        try:
            msg = await channel.fetch_message(message_id)
        except:
            await ctx.send("❌ Message not found!")
            return
        
        winners_list = []
        for reaction in msg.reactions:
            if reaction.emoji == "🎉":
                async for user in reaction.users():
                    if not user.bot:
                        winners_list.append(user)
        
        if not winners_list:
            await ctx.send("❌ No entries!")
            return
        
        winners = random.sample(winners_list, min(num_winners, len(winners_list)))
        winner_mentions = ', '.join([w.mention for w in winners])
        
        embed = discord.Embed(title="🎉 GIVEAWAY ENDED", description=f"Prize: **{prize}**\nWinners: {winner_mentions}", color=0x00ff00)
        await channel.send(embed=embed)
        
        cursor.execute('UPDATE giveaways SET status = ? WHERE message_id = ?', ('ended', message_id))
        self.db.commit()
        
        await ctx.send("✅ Giveaway ended!")

    @giveaway.command(name='reroll')
    @commands.has_permissions(administrator=True)
    async def reroll_giveaway(self, ctx, message_id: int):
        """Reroll giveaway winners"""
        cursor = self.db.cursor()
        cursor.execute('SELECT channel_id, prize, winners FROM giveaways WHERE message_id = ?', (message_id,))
        result = cursor.fetchone()
        
        if not result:
            await ctx.send("❌ Giveaway not found!")
            return
        
        channel_id, prize, num_winners = result
        channel = self.bot.get_channel(channel_id)
        
        try:
            msg = await channel.fetch_message(message_id)
        except:
            await ctx.send("❌ Message not found!")
            return
        
        winners_list = []
        for reaction in msg.reactions:
            if reaction.emoji == "🎉":
                async for user in reaction.users():
                    if not user.bot:
                        winners_list.append(user)
        
        if not winners_list:
            await ctx.send("❌ No entries!")
            return
        
        winners = random.sample(winners_list, min(num_winners, len(winners_list)))
        winner_mentions = ', '.join([w.mention for w in winners])
        
        embed = discord.Embed(title="🎉 GIVEAWAY REROLLED", description=f"Prize: **{prize}**\nNew Winners: {winner_mentions}", color=0x00ff00)
        await channel.send(embed=embed)
        await ctx.send("✅ Winners rerolled!")

async def setup(bot):
    await bot.add_cog(Giveaway(bot))