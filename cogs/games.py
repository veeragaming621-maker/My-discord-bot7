import discord
from discord.ext import commands
import random

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}

    @commands.group(invoke_without_command=True)
    async def game(self, ctx):
        """Game commands"""
        embed = discord.Embed(title="🎮 Games", description="Have fun with games!", color=0x00ffff)
        embed.add_field(name="!game guess", value="Guess the number game (1-100)", inline=False)
        embed.add_field(name="!game rps <choice>", value="Rock Paper Scissors", inline=False)
        embed.add_field(name="!game coin", value="Flip a coin", inline=False)
        embed.add_field(name="!game roll [sides]", value="Roll a dice", inline=False)
        await ctx.send(embed=embed)

    @game.command(name='guess')
    async def guess_number(self, ctx):
        """Guess the number game"""
        if ctx.author.id in self.active_games:
            await ctx.send("❌ You already have an active game!")
            return
        
        number = random.randint(1, 100)
        
        try:
            embed = discord.Embed(title="🎮 Guess The Number", description="I've picked a number between 1-100. You have 10 guesses!\nGuess in this DM channel.", color=0x00ffff)
            await ctx.author.send(embed=embed)
            
            self.active_games[ctx.author.id] = {'number': number, 'guesses': 0, 'channel': ctx.channel}
            await ctx.send(f"✅ Check your DMs, {ctx.author.mention}! Game started!")
            
        except discord.Forbidden:
            await ctx.send("❌ I cannot send DMs to you!")

    @game.command(name='rps')
    async def rock_paper_scissors(self, ctx, choice: str):
        """Play rock paper scissors"""
        choices = ['rock', 'paper', 'scissors']
        choice = choice.lower()
        
        if choice not in choices:
            await ctx.send("❌ Use: rock, paper, or scissors")
            return
        
        bot_choice = random.choice(choices)
        
        embed = discord.Embed(title="🎮 Rock Paper Scissors", color=0x00ffff)
        embed.add_field(name="Your Choice", value=choice.capitalize(), inline=True)
        embed.add_field(name="Bot Choice", value=bot_choice.capitalize(), inline=True)
        
        if choice == bot_choice:
            embed.add_field(name="Result", value="🤝 It's a tie!", inline=False)
            embed.color = 0xffff00
        elif (choice == 'rock' and bot_choice == 'scissors') or (choice == 'paper' and bot_choice == 'rock') or (choice == 'scissors' and bot_choice == 'paper'):
            embed.add_field(name="Result", value="✅ You won!", inline=False)
            embed.color = 0x00ff00
        else:
            embed.add_field(name="Result", value="❌ You lost!", inline=False)
            embed.color = 0xff0000
        
        await ctx.send(embed=embed)

    @game.command(name='coin')
    async def coin_flip(self, ctx):
        """Flip a coin"""
        result = random.choice(['Heads', 'Tails'])
        embed = discord.Embed(title="🪙 Coin Flip", description=f"Result: **{result}**", color=0xffff00)
        await ctx.send(embed=embed)

    @game.command(name='roll')
    async def dice_roll(self, ctx, sides: int = 6):
        """Roll a dice"""
        if sides < 2:
            await ctx.send("❌ Dice must have at least 2 sides!")
            return
        
        result = random.randint(1, sides)
        embed = discord.Embed(title="🎲 Dice Roll", description=f"D{sides}: **{result}**", color=0x00ffff)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Games(bot))