import discord
from discord.ext import commands
import sqlite3

class Extra(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('bot.db')
        self.setup_db()

    def setup_db(self):
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS autoresponder (
                guild_id INTEGER,
                trigger TEXT,
                response TEXT,
                PRIMARY KEY (guild_id, trigger)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS autorole (
                guild_id INTEGER,
                role_id INTEGER,
                PRIMARY KEY (guild_id, role_id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS noprefixperms (
                guild_id INTEGER,
                user_id INTEGER,
                PRIMARY KEY (guild_id, user_id)
            )
        ''')
        self.db.commit()

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def autoresponse(self, ctx):
        """Auto-responder commands"""
        embed = discord.Embed(title="🤖 Auto-Responder", description="Automatically respond to messages", color=0x00ffff)
        embed.add_field(name="!autoresponse add <trigger> <response>", value="Add auto-response", inline=False)
        embed.add_field(name="!autoresponse remove <trigger>", value="Remove auto-response", inline=False)
        embed.add_field(name="!autoresponse list", value="List auto-responses", inline=False)
        await ctx.send(embed=embed)

    @autoresponse.command(name='add')
    async def add_autoresponse(self, ctx, trigger: str, *, response: str):
        """Add auto-response"""
        cursor = self.db.cursor()
        cursor.execute('INSERT OR REPLACE INTO autoresponder (guild_id, trigger, response) VALUES (?, ?, ?)',
                      (ctx.guild.id, trigger.lower(), response))
        self.db.commit()
        await ctx.send(f"✅ Auto-response added for '{trigger}'")

    @autoresponse.command(name='list')
    async def list_autoresponse(self, ctx):
        """List auto-responses"""
        cursor = self.db.cursor()
        cursor.execute('SELECT trigger, response FROM autoresponder WHERE guild_id = ?', (ctx.guild.id,))
        responses = cursor.fetchall()
        
        if not responses:
            await ctx.send("❌ No auto-responses set!")
            return
        
        embed = discord.Embed(title="📋 Auto-Responses", color=0x00ffff)
        for trigger, response in responses:
            embed.add_field(name=trigger, value=response[:100], inline=False)
        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def autorole(self, ctx):
        """Auto-role commands"""
        embed = discord.Embed(title="👤 Auto-Role", description="Automatically assign roles to new members", color=0x00ff99)
        embed.add_field(name="!autorole add <role>", value="Add auto-role", inline=False)
        embed.add_field(name="!autorole list", value="List auto-roles", inline=False)
        await ctx.send(embed=embed)

    @autorole.command(name='add')
    async def add_autorole(self, ctx, role: discord.Role):
        """Add auto-role"""
        cursor = self.db.cursor()
        cursor.execute('INSERT OR REPLACE INTO autorole (guild_id, role_id) VALUES (?, ?)',
                      (ctx.guild.id, role.id))
        self.db.commit()
        await ctx.send(f"✅ Auto-role added: {role.mention}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle autoresponse"""
        if message.author.bot or not message.guild:
            return
        
        cursor = self.db.cursor()
        cursor.execute('SELECT response FROM autoresponder WHERE guild_id = ? AND trigger = ?',
                      (message.guild.id, message.content.lower()))
        response = cursor.fetchone()
        if response:
            await message.reply(response[0])

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Assign autoroles"""
        cursor = self.db.cursor()
        cursor.execute('SELECT role_id FROM autorole WHERE guild_id = ?', (member.guild.id,))
        roles = cursor.fetchall()
        
        for (role_id,) in roles:
            role = member.guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role)
                except:
                    pass

async def setup(bot):
    await bot.add_cog(Extra(bot))