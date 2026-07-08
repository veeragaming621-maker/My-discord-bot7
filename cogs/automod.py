import discord
from discord.ext import commands
import sqlite3

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('bot.db')
        self.setup_db()

    def setup_db(self):
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automod_settings (
                guild_id INTEGER PRIMARY KEY,
                all_caps BOOLEAN DEFAULT 0,
                invites BOOLEAN DEFAULT 0,
                links BOOLEAN DEFAULT 0,
                mentions BOOLEAN DEFAULT 0
            )
        ''')
        self.db.commit()

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def automod(self, ctx):
        """AutoMod settings"""
        embed = discord.Embed(title="🤖 AutoMod Settings", color=0xff0000)
        embed.add_field(name="!automod allcaps <on/off>", value="Detect ALL CAPS", inline=False)
        embed.add_field(name="!automod invites <on/off>", value="Block invites", inline=False)
        embed.add_field(name="!automod links <on/off>", value="Block links", inline=False)
        embed.add_field(name="!automod status", value="View settings", inline=False)
        await ctx.send(embed=embed)

    @automod.command(name='allcaps')
    @commands.has_permissions(administrator=True)
    async def all_caps(self, ctx, setting: str):
        """Toggle ALL CAPS detection"""
        setting = setting.lower() in ['on', '1', 'true', 'yes']
        cursor = self.db.cursor()
        cursor.execute('INSERT OR REPLACE INTO automod_settings (guild_id, all_caps) VALUES (?, ?)',
                      (ctx.guild.id, setting))
        self.db.commit()
        status = "✅ ENABLED" if setting else "❌ DISABLED"
        await ctx.send(f"ALL CAPS detection {status}")

    @automod.command(name='invites')
    @commands.has_permissions(administrator=True)
    async def invite_links(self, ctx, setting: str):
        """Toggle invite blocking"""
        setting = setting.lower() in ['on', '1', 'true', 'yes']
        cursor = self.db.cursor()
        cursor.execute('INSERT OR REPLACE INTO automod_settings (guild_id, invites) VALUES (?, ?)',
                      (ctx.guild.id, setting))
        self.db.commit()
        status = "✅ ENABLED" if setting else "❌ DISABLED"
        await ctx.send(f"Invite blocking {status}")

    @automod.command(name='links')
    @commands.has_permissions(administrator=True)
    async def all_links(self, ctx, setting: str):
        """Toggle all links blocking"""
        setting = setting.lower() in ['on', '1', 'true', 'yes']
        cursor = self.db.cursor()
        cursor.execute('INSERT OR REPLACE INTO automod_settings (guild_id, links) VALUES (?, ?)',
                      (ctx.guild.id, setting))
        self.db.commit()
        status = "✅ ENABLED" if setting else "❌ DISABLED"
        await ctx.send(f"Link blocking {status}")

    @automod.command(name='status')
    @commands.has_permissions(administrator=True)
    async def mod_status(self, ctx):
        """View AutoMod settings"""
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM automod_settings WHERE guild_id = ?', (ctx.guild.id,))
        result = cursor.fetchone()
        
        embed = discord.Embed(title="🤖 AutoMod Status", color=0xff0000)
        
        if result:
            _, caps, invites, links, mentions = result
            embed.add_field(name="ALL CAPS", value="✅" if caps else "❌", inline=True)
            embed.add_field(name="Invite Links", value="✅" if invites else "❌", inline=True)
            embed.add_field(name="All Links", value="✅" if links else "❌", inline=True)
        else:
            embed.description = "No settings configured"
        
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Monitor messages for AutoMod violations"""
        if message.author.bot or not message.guild:
            return
        
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM automod_settings WHERE guild_id = ?', (ctx.guild.id,))
        result = cursor.fetchone()
        
        if not result:
            return
        
        _, caps, invites, links, mentions = result
        
        action_taken = False
        reason = ""
        
        if caps and len(message.content) > 5 and message.content.isupper():
            reason = "Excessive caps"
            action_taken = True
        
        if invites and ("discord.gg/" in message.content or "discord.com/invite/" in message.content):
            reason = "Invite link"
            action_taken = True
        
        if links and ("http://" in message.content or "https://" in message.content):
            if not message.author.guild_permissions.administrator:
                reason = "Link detected"
                action_taken = True
        
        if action_taken:
            try:
                await message.delete()
                embed = discord.Embed(title="⚠️ Message Deleted", description=f"**User:** {message.author.mention}\n**Reason:** {reason}", color=0xff0000)
                await message.channel.send(embed=embed, delete_after=5)
            except:
                pass

async def setup(bot):
    await bot.add_cog(AutoMod(bot))