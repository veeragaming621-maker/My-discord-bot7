import discord
from discord.ext import commands
import sqlite3

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('bot.db')
        self.setup_db()

    def setup_db(self):
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id INTEGER PRIMARY KEY,
                guild_id INTEGER,
                user_id INTEGER,
                channel_id INTEGER,
                status TEXT
            )
        ''')
        self.db.commit()

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def ticket(self, ctx):
        """Ticket system commands"""
        embed = discord.Embed(title="🎫 Ticket System", color=0xff6600)
        embed.add_field(name="!ticket setup", value="Setup ticket panel", inline=False)
        embed.add_field(name="!ticket close", value="Close a ticket", inline=False)
        await ctx.send(embed=embed)

    @ticket.command(name='setup')
    @commands.has_permissions(administrator=True)
    async def setup_tickets(self, ctx):
        """Setup ticket panel"""
        embed = discord.Embed(title="🎫 Support Tickets", description="Click the button below to create a ticket!", color=0xff6600)
        
        view = TicketView(self.bot, ctx.guild.id, self.db)
        await ctx.send(embed=embed, view=view)
        await ctx.send("✅ Ticket panel created!")

    @ticket.command(name='close')
    @commands.has_permissions(administrator=True)
    async def close_ticket(self, ctx):
        """Close a ticket"""
        cursor = self.db.cursor()
        cursor.execute('SELECT ticket_id FROM tickets WHERE channel_id = ?', (ctx.channel.id,))
        result = cursor.fetchone()
        
        if not result:
            await ctx.send("❌ This is not a ticket!")
            return
        
        await ctx.channel.delete()

class TicketView(discord.ui.View):
    def __init__(self, bot, guild_id, db):
        super().__init__(timeout=None)
        self.bot = bot
        self.guild_id = guild_id
        self.db = db
        self.ticket_count = 0

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.primary, emoji="🎫")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = self.bot.get_guild(self.guild_id)
        
        ticket_category = discord.utils.get(guild.categories, name="Tickets")
        if not ticket_category:
            ticket_category = await guild.create_category("Tickets")
        
        self.ticket_count += 1
        channel = await ticket_category.create_text_channel(name=f"ticket-{interaction.user.name}")
        
        await channel.set_permissions(guild.default_role, view_channel=False)
        await channel.set_permissions(interaction.user, view_channel=True, send_messages=True)
        
        cursor = self.db.cursor()
        cursor.execute('INSERT INTO tickets (guild_id, user_id, channel_id, status) VALUES (?, ?, ?, ?)',
                      (guild.id, interaction.user.id, channel.id, 'open'))
        self.db.commit()
        
        embed = discord.Embed(title="🎫 Support Ticket", description=f"Welcome {interaction.user.mention}!\n\nHow can we help you?", color=0xff6600)
        await channel.send(embed=embed)
        
        await interaction.response.send_message(f"✅ Ticket created: {channel.mention}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))