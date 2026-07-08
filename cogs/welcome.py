import discord
from discord.ext import commands
import sqlite3

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('bot.db')
        self.setup_db()

    def setup_db(self):
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS welcome_settings (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER,
                welcome_text TEXT,
                image_url TEXT
            )
        ''')
        self.db.commit()

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx):
        """Welcome system commands"""
        embed = discord.Embed(title="Welcome System", color=0x2f3136)
        embed.add_field(name="!welcome channel <#channel>", value="Set welcome channel", inline=False)
        embed.add_field(name="!welcome text <text>", value="Set welcome text", inline=False)
        embed.add_field(name="!welcome image <url>", value="Set welcome image", inline=False)
        embed.add_field(name="!welcome test", value="Test welcome message", inline=False)
        embed.add_field(name="!welcome view", value="View settings", inline=False)
        await ctx.send(embed=embed)

    @welcome.command(name='channel')
    @commands.has_permissions(administrator=True)
    async def set_channel(self, ctx, channel: discord.TextChannel):
        """Set welcome channel"""
        cursor = self.db.cursor()
        cursor.execute('INSERT OR REPLACE INTO welcome_settings (guild_id, channel_id) VALUES (?, ?)',
                      (ctx.guild.id, channel.id))
        self.db.commit()
        await ctx.send(f"✅ Welcome channel set to {channel.mention}")

    @welcome.command(name='text')
    @commands.has_permissions(administrator=True)
    async def set_text(self, ctx, *, text):
        """Set welcome text"""
        cursor = self.db.cursor()
        cursor.execute('INSERT OR REPLACE INTO welcome_settings (guild_id, welcome_text) VALUES (?, ?)',
                      (ctx.guild.id, text))
        self.db.commit()
        await ctx.send(f"✅ Welcome text updated!")

    @welcome.command(name='test')
    @commands.has_permissions(administrator=True)
    async def test_welcome(self, ctx):
        """Test welcome message"""
        cursor = self.db.cursor()
        cursor.execute('SELECT channel_id, welcome_text FROM welcome_settings WHERE guild_id = ?',
                      (ctx.guild.id,))
        result = cursor.fetchone()
        
        if not result:
            await ctx.send("❌ Welcome not configured!")
            return
        
        channel_id, text = result
        channel = self.bot.get_channel(channel_id)
        
        if not channel:
            await ctx.send("❌ Welcome channel not found!")
            return
        
        welcome_text = text.format(user=ctx.author.mention, guild=ctx.guild.name) if text else "Welcome!"
        embed = discord.Embed(title="Welcome!", description=welcome_text, color=0x00ff00)
        await channel.send(embed=embed)
        await ctx.send("✅ Test message sent!")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Send welcome message when member joins"""
        cursor = self.db.cursor()
        cursor.execute('SELECT channel_id, welcome_text FROM welcome_settings WHERE guild_id = ?',
                      (member.guild.id,))
        result = cursor.fetchone()
        
        if not result:
            return
        
        channel_id, text = result
        channel = self.bot.get_channel(channel_id)
        
        if not channel:
            return
        
        welcome_text = text.format(user=member.mention, guild=member.guild.name) if text else f"Welcome {member.mention}!"
        embed = discord.Embed(title="Welcome!", description=welcome_text, color=0x00ff00)
        embed.set_footer(text=f"Member #{member.guild.member_count}")
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))